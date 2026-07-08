#!/usr/bin/env python3
"""
NETCONF-YANG Query Tool for Cisco Routers
Allows interactive querying with vim editor for payload input
Includes response time tracking
"""

import os
import sys
import tempfile
import subprocess
import getpass
import time
from datetime import datetime
from ncclient import manager
from ncclient.operations import RPCError
import xml.dom.minidom

def get_device_credentials():
    """Prompt user for device connection details"""
    print("=== NETCONF Device Connection ===")
    host = input("Device IP Address: ").strip()
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    
    return host, username, password

def edit_with_vim():
    """Open vim editor to create/edit the NETCONF payload"""
    example_payload = """<!-- NETCONF-YANG Query Editor -->
<!-- 
Example - Get config for a specific interface (will be wrapped in get-config:
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
  <interface>
    <name>GigabitEthernet0</name>
  </interface>
</interfaces>
-->

"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as tmp_file:
        tmp_file.write(example_payload)
        tmp_file_path = tmp_file.name
    
    try:
        subprocess.run(['vim', tmp_file_path], check=True)
        
        with open(tmp_file_path, 'r') as file:
            content = file.read().strip()
        
        # Remove comments and empty lines
        lines = [line for line in content.split('\n') 
                if not line.strip().startswith('<!--') and 
                   not line.strip().endswith('-->') and 
                   line.strip()]
        
        payload = '\n'.join(lines)
        
        if not payload:
            print("No payload entered. Exiting.")
            return None
            
        return payload
        
    except subprocess.CalledProcessError:
        print("Error: vim editor was cancelled or failed")
        return None
    except FileNotFoundError:
        print("Error: vim not found. Please install vim or modify the script to use another editor")
        return None
    finally:
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

def prettify_xml(xml_string):
    """Format XML for better readability"""
    try:
        dom = xml.dom.minidom.parseString(xml_string)
        return dom.toprettyxml(indent="  ")
    except:
        return xml_string

def format_duration(duration_seconds):
    """Format duration in a human-readable way"""
    if duration_seconds < 1:
        return f"{duration_seconds*1000:.2f} ms"
    elif duration_seconds < 60:
        return f"{duration_seconds:.2f} seconds"
    else:
        minutes = int(duration_seconds // 60)
        seconds = duration_seconds % 60
        return f"{minutes}m {seconds:.2f}s"

def execute_netconf_query(host, username, password, payload):
    """Execute the NETCONF query on the device with timing"""
    connection_start_time = time.time()
    
    try:
        print(f"\n=== Connecting to {host} ===")
        
        with manager.connect(
            host=host,
            port=830,
            username=username,
            password=password,
            device_params={'name': 'csr'},
            hostkey_verify=False,
            look_for_keys=False,
            allow_agent=False
        ) as m:
            connection_time = time.time() - connection_start_time
            print(f"✓ Connected successfully (Connection time: {format_duration(connection_time)})")
            
            print("\n=== Sending Query ===")
            print(payload)
            print("\n" + "="*50)
            
            # Record query start time
            query_start_time = time.time()
            query_timestamp = datetime.now()
            
            try:
                # Always use get-config with running source and subtree filter
                print("Using get-config with running source and subtree filter")
                result = m.get_config(source='running', filter=('subtree', payload))
                
                # Calculate timing
                query_end_time = time.time()
                query_duration = query_end_time - query_start_time
                total_duration = query_end_time - connection_start_time
                
                # Display timing information
                print("\n=== Timing Information ===")
                print(f"Query started:     {query_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
                print(f"Query completed:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
                print(f"Connection time:   {format_duration(connection_time)}")
                print(f"Query time:        {format_duration(query_duration)}")
                print(f"Total time:        {format_duration(total_duration)}")
                
                # Performance indicator
                if query_duration < 1:
                    perf_indicator = "🚀 Fast"
                elif query_duration < 5:
                    perf_indicator = "✅ Good"
                elif query_duration < 15:
                    perf_indicator = "⚠️  Slow"
                else:
                    perf_indicator = "🐌 Very Slow"
                
                print(f"Performance:       {perf_indicator}")
                
                print("\n=== Response ===")
                formatted_response = prettify_xml(str(result))
                print(formatted_response)
                
                # Save response to file
                timestamp_str = query_timestamp.strftime('%Y%m%d_%H%M%S')
                filename = f"netconf_response_{timestamp_str}.xml"
                
                header = f"""<!--
NETCONF Query Response
Device: {host}
Query Time: {query_timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Connection Duration: {format_duration(connection_time)}
Query Duration: {format_duration(query_duration)}
Total Duration: {format_duration(total_duration)}
Performance: {perf_indicator}

Original Query:
{payload}
-->

"""
                
                with open(filename, 'w') as f:
                    f.write(header)
                    f.write(formatted_response)
                
                print(f"\n✓ Response saved to: {filename}")
                
                # Summary statistics
                response_size = len(formatted_response)
                print(f"\n=== Summary ===")
                print(f"Response size:     {response_size:,} bytes")
                if query_duration > 0:
                    throughput = response_size / query_duration
                    print(f"Throughput:        {throughput:,.0f} bytes/second")
                
            except RPCError as e:
                query_duration = time.time() - query_start_time
                print(f"\n❌ NETCONF RPC Error (after {format_duration(query_duration)}): {e}")
                print("\n=== Troubleshooting Suggestions ===")
                print("1. Check if the YANG model is supported on this device")
                print("2. Verify the namespace URIs are correct")
                print("3. Try a simpler query path")
                print("4. Check if the data exists in running config")
            except Exception as e:
                query_duration = time.time() - query_start_time
                print(f"\n❌ Query execution error (after {format_duration(query_duration)}): {e}")
                
    except Exception as e:
        connection_duration = time.time() - connection_start_time
        print(f"\n❌ Connection error (after {format_duration(connection_duration)}): {e}")

def display_session_stats(session_stats):
    """Display session statistics"""
    if not session_stats:
        return
    
    print("\n=== Session Statistics ===")
    print(f"Total queries:     {len(session_stats)}")
    
    query_times = [stat['query_time'] for stat in session_stats]
    if query_times:
        avg_time = sum(query_times) / len(query_times)
        min_time = min(query_times)
        max_time = max(query_times)
        
        print(f"Average query time: {format_duration(avg_time)}")
        print(f"Fastest query:      {format_duration(min_time)}")
        print(f"Slowest query:      {format_duration(max_time)}")
        
        total_session_time = sum(query_times)
        print(f"Total query time:   {format_duration(total_session_time)}")

def main():
    """Main function"""
    print("NETCONF-YANG Query Tool for Cisco Routers")
    print("(Simplified - Always uses get-config)")
    print("=" * 45)
    
    session_stats = []
    
    try:
        host, username, password = get_device_credentials()
        
        while True:
            print("\n=== Query Options ===")
            print("1. Create new query (vim editor)")
            print("2. Show session statistics")
            print("3. Exit")
            
            choice = input("\nSelect option (1-3): ").strip()
            
            if choice == '1':
                payload = edit_with_vim()
                if payload:
                    query_start = time.time()
                    execute_netconf_query(host, username, password, payload)
                    query_time = time.time() - query_start
                    
                    session_stats.append({
                        'timestamp': datetime.now(),
                        'query_time': query_time,
                        'host': host
                    })
                    
                    if input("\nPerform another query? (y/n): ").lower() != 'y':
                        break
                        
            elif choice == '2':
                display_session_stats(session_stats)
                
            elif choice == '3':
                display_session_stats(session_stats)
                print("Goodbye!")
                break
            else:
                print("Invalid option. Please select 1-3.")
                
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        display_session_stats(session_stats)
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()