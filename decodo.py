import requests
from pathlib import Path
import urllib3
import json
import base64
from requests.auth import HTTPProxyAuth
import requests.auth

# Disable SSL warnings (since we're using verify=False like curl -k)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# #region agent log
LOG_PATH = '/Users/janmunts/Documents/business/axis data labs/customers/media removal/screenshot-service/.cursor/debug.log'
def debug_log(location, message, data, hypothesis_id):
    try:
        with open(LOG_PATH, 'a') as f:
            log_entry = {
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': hypothesis_id,
                'location': location,
                'message': message,
                'data': data,
                'timestamp': __import__('time').time() * 1000
            }
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
# #endregion

# Decodo proxy configuration
username = 'U0000335470'
password = 'PW_1e23e206f5802a65cb90e2e89598d8dbb'

# Target URL to screenshot
target_url = 'https://www.glassdoor.com/Reviews/Employee-Review-Wise-E637715-RVW94482642.htm'

# Create output directory
output_dir = Path('output/screenshots')
output_dir.mkdir(parents=True, exist_ok=True)

# #region agent log
debug_log('decodo.py:19', 'Proxy config setup', {'username': username, 'proxy_host': 'unblock.decodo.com', 'proxy_port': 60000}, 'A')
# #endregion

# Test Hypothesis A: Use HTTP proxy format instead of HTTPS
proxy_http = f"http://{username}:{password}@unblock.decodo.com:60000"
proxy_https_embedded = f"https://{username}:{password}@unblock.decodo.com:60000"
proxy_base = "http://unblock.decodo.com:60000"
proxy_base_https = "https://unblock.decodo.com:60000"  # Test HTTPS proxy URL format

# #region agent log
debug_log('decodo.py:26', 'Proxy URL formats created', {'proxy_http': proxy_http[:50] + '...', 'proxy_base': proxy_base}, 'A')
# #endregion

# Headers - use 'png' for PNG output format
headers = {
    'X-SU-Headless': 'png'
}

# #region agent log
debug_log('decodo.py:32', 'Request attempt starting', {'target_url': target_url, 'headers': headers}, 'A')
# #endregion

# Make request through proxy
print(f"Taking screenshot of {target_url}...")

response = None
screenshot_data = None

# Test Hypothesis D: Use Web Scraping API endpoint (correct endpoint: /v2/scrape)
# According to https://help.decodo.com/docs/screenshot, screenshots use the Web Scraping API
try:
    # #region agent log
    debug_log('decodo.py:73', 'Attempting Web Scraping API endpoint', {'api_endpoint': 'scraper-api.decodo.com/v2/scrape'}, 'D')
    # #endregion
    
    # Create Basic Auth header
    auth_string = base64.b64encode(f'{username}:{password}'.encode()).decode()
    
    api_url = 'https://scraper-api.decodo.com/v2/scrape'
    api_headers = {
        'Accept': 'application/json',
        'Authorization': f'Basic {auth_string}',
        'Content-Type': 'application/json'
    }
    api_data = {
        'target': 'universal',
        'url': target_url,
        'screenshot': True  # Request screenshot (PNG format)
    }
    
    # #region agent log
    debug_log('decodo.py:88', 'Sending POST request to Web Scraping API', {'url': api_url, 'url_param': target_url}, 'D')
    # #endregion
    
    api_response = requests.post(api_url, headers=api_headers, json=api_data, timeout=180)
    
    # #region agent log
    debug_log('decodo.py:93', 'Web Scraping API response received', {'status_code': api_response.status_code, 'content_type': api_response.headers.get('Content-Type', 'unknown')}, 'D')
    # #endregion
    
    if api_response.status_code == 200:
        result = api_response.json()
        # #region agent log
        debug_log('decodo.py:98', 'Parsing API response', {'has_results': 'results' in result, 'response_keys': list(result.keys())[:5]}, 'D')
        # #endregion
        
        # The response contains results array with screenshot in first result
        if 'results' in result and result['results'] and len(result['results']) > 0:
            first_result = result['results'][0]
            # #region agent log
            debug_log('decodo.py:103', 'Checking first result for screenshot', {'has_screenshot': 'screenshot' in first_result}, 'D')
            # #endregion
            
            if 'screenshot' in first_result:
                screenshot_data = base64.b64decode(first_result['screenshot'])
                # #region agent log
                debug_log('decodo.py:108', 'Screenshot decoded successfully', {'decoded_size': len(screenshot_data)}, 'D')
                # #endregion
            else:
                # #region agent log
                debug_log('decodo.py:111', 'No screenshot in first result', {'result_keys': list(first_result.keys())[:5]}, 'D')
                # #endregion
                raise ValueError("No screenshot field in API response results")
        else:
            # #region agent log
            debug_log('decodo.py:116', 'No results array in response', {'response_keys': list(result.keys())[:5]}, 'D')
            # #endregion
            raise ValueError("No results array in API response")
    else:
        # #region agent log
        debug_log('decodo.py:121', 'Web Scraping API error', {'status_code': api_response.status_code, 'response_text': api_response.text[:200]}, 'D')
        # #endregion
        api_response.raise_for_status()
        
except Exception as e:
    # #region agent log
    debug_log('decodo.py:108', 'Web Scraping API failed, trying Site Unblocker', {'error_type': type(e).__name__, 'error_msg': str(e)[:200]}, 'D')
    # #endregion
    
    # Fallback to Site Unblocker (original approach)
    # Test Hypothesis G: Use proxy without embedded auth, add Proxy-Authorization header manually (matches curl -U)
    try:
        # #region agent log
        debug_log('decodo.py:133', 'Attempting Site Unblocker with Proxy-Authorization header', {'proxy_base': proxy_base, 'method': 'manual Proxy-Authorization header'}, 'G')
        # #endregion
        # Create Proxy-Authorization header manually (equivalent to curl -U)
        proxy_auth_header = base64.b64encode(f'{username}:{password}'.encode()).decode()
        headers_with_proxy_auth = headers.copy()
        headers_with_proxy_auth['Proxy-Authorization'] = f'Basic {proxy_auth_header}'
        
        response = requests.get(
            target_url,
            proxies={
                'http': proxy_base,
                'https': proxy_base
            },
            headers=headers_with_proxy_auth,
            verify=False,  # -k flag in curl means don't verify SSL
            timeout=(30, 180)  # (connect, read) timeout tuple
        )
        # #region agent log
        debug_log('decodo.py:153', 'Site Unblocker with Proxy-Authorization header completed', {'status_code': response.status_code, 'content_length': len(response.content)}, 'G')
        # #endregion
    except Exception as e2:
        # #region agent log
        debug_log('decodo.py:156', 'Proxy-Authorization header method failed, trying embedded auth', {'error_type': type(e2).__name__, 'error_msg': str(e2)[:200]}, 'G')
        # #endregion
        
        # Test Hypothesis B: Try HTTP proxy format with embedded auth (original approach)
        try:
            # #region agent log
            debug_log('decodo.py:156', 'Attempting Site Unblocker with HTTP proxy format', {'proxy_format': 'http://user:pass@host:port', 'timeout': 180}, 'B')
            # #endregion
            response = requests.get(
                target_url,
                proxies={
                    'http': proxy_http,
                    'https': proxy_http  # Use HTTP proxy format even for HTTPS targets
                },
                headers=headers,
                verify=False,  # -k flag in curl means don't verify SSL
                timeout=180  # Increased timeout for screenshot rendering
            )
            # #region agent log
            debug_log('decodo.py:170', 'Site Unblocker request completed', {'status_code': response.status_code, 'content_length': len(response.content)}, 'B')
            # #endregion
        except Exception as e2b:
            # #region agent log
            debug_log('decodo.py:173', 'Site Unblocker HTTP proxy failed, trying separate auth', {'error_type': type(e2b).__name__}, 'B')
            # #endregion
            
            # Test Hypothesis C: Try with separate auth parameter (HTTP proxy base)
        try:
            # #region agent log
            debug_log('decodo.py:154', 'Attempting Site Unblocker with separate proxy auth (HTTP base)', {'proxy_base': proxy_base}, 'C')
            # #endregion
            proxy_auth = HTTPProxyAuth(username, password)
            response = requests.get(
                target_url,
                proxies={
                    'http': proxy_base,
                    'https': proxy_base
                },
                auth=proxy_auth,
                headers=headers,
                verify=False,
                timeout=30
            )
            # #region agent log
            debug_log('decodo.py:169', 'Site Unblocker separate auth (HTTP) succeeded', {'status_code': response.status_code}, 'C')
            # #endregion
        except Exception as e3:
            # #region agent log
            debug_log('decodo.py:172', 'HTTP proxy base with separate auth failed', {'error_type': type(e3).__name__, 'error_msg': str(e3)[:200]}, 'C')
            # #endregion
            
            # Test Hypothesis E: Try HTTPS proxy URL format with separate auth (matches curl -x https://)
            try:
                # #region agent log
                debug_log('decodo.py:177', 'Attempting Site Unblocker with HTTPS proxy URL and separate auth', {'proxy_base_https': proxy_base_https}, 'E')
                # #endregion
                proxy_auth = HTTPProxyAuth(username, password)
                response = requests.get(
                    target_url,
                    proxies={
                        'http': proxy_base_https,
                        'https': proxy_base_https
                    },
                    auth=proxy_auth,
                    headers=headers,
                    verify=False,
                    timeout=30
                )
                # #region agent log
                debug_log('decodo.py:192', 'HTTPS proxy URL with separate auth succeeded', {'status_code': response.status_code}, 'E')
                # #endregion
            except Exception as e4:
                # #region agent log
                debug_log('decodo.py:195', 'All proxy methods failed', {'last_error_type': type(e4).__name__, 'last_error_msg': str(e4)[:200]}, 'E')
                # #endregion
                raise e4

# Save PNG file (either from Web Scraping API or Site Unblocker)
if screenshot_data:
    # Save screenshot from Web Scraping API
    filename = target_url.replace('https://', '').replace('http://', '').replace('/', '_')[:50] + '.png'
    output_path = output_dir / filename
    
    with open(output_path, 'wb') as f:
        f.write(screenshot_data)
    
    print(f"Screenshot saved to: {output_path}")
    print(f"File size: {len(screenshot_data)} bytes")
elif response and response.status_code == 200:
    # Save screenshot from Site Unblocker
    filename = target_url.replace('https://', '').replace('http://', '').replace('/', '_')[:50] + '.png'
    output_path = output_dir / filename
    
    with open(output_path, 'wb') as f:
        f.write(response.content)
    
    print(f"Screenshot saved to: {output_path}")
    print(f"File size: {len(response.content)} bytes")
else:
    if response:
        print(f"Error: Status code {response.status_code}")
        print(response.text[:500])
    else:
        print("Error: Failed to get screenshot from any method")

