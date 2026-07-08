# NETCONF-YANG Query Tool for Cisco Routers

A Python-based interactive tool for querying Cisco routers using NETCONF/YANG protocols. This tool provides a user-friendly interface with vim editor integration for crafting YANG queries and includes comprehensive response time tracking.

## Features

- **Interactive NETCONF querying** with real-time connection to Cisco devices
- **Vim editor integration** for creating and editing YANG XML payloads
- **Performance monitoring** with detailed timing statistics
- **Response formatting** with pretty-printed XML output
- **Automatic file saving** of query responses with metadata
- **Session statistics** tracking across multiple queries
- **Built-in examples** for common YANG queries
- **Error handling** with troubleshooting suggestions

## Prerequisites

### Required Dependencies

```bash
pip install ncclient
```

### System Requirements

- Python 3.6 or higher
- vim editor installed and accessible from command line
- Network access to target Cisco devices on port 830 (NETCONF)

### Supported Devices

- Cisco IOS-XE routers with NETCONF/YANG support
- Devices must have NETCONF enabled on port 830

## Installation

1. Clone or download the script:
```bash
git clone <repository-url>
cd Tools/Tools/python
```

2. Install required Python packages:
```bash
pip install ncclient
```

3. Make the script executable:
```bash
chmod +x query-yang.py
```

## Usage

### Basic Usage

Run the tool:
```bash
python3 query-yang.py
```

### Workflow

1. **Device Connection**: Enter device IP, username, and password
2. **Query Creation**: Use vim editor to create YANG XML queries
3. **Execution**: Tool automatically wraps queries in get-config operations
4. **Results**: View formatted responses and timing statistics
5. **File Output**: Responses saved automatically with metadata

### Example Queries

#### Get All Interfaces
```xml
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/>
```

#### Get Specific Interface
```xml
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
  <interface>
    <name>GigabitEthernet0</name>
  </interface>
</interfaces>
```

#### Get NAT Configuration
```xml
<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native" xmlns:ios-nat="http://cisco.com/ns/yang/Cisco-IOS-XE-nat">
  <ip>
    <ios-nat:nat/>
  </ip>
</native>
```

## Output Files

The tool automatically saves query responses with the following naming convention:
```
netconf_response_YYYYMMDD_HHMMSS.xml
```

Each file includes:
- Original query XML
- Complete device response
- Timing metadata
- Performance indicators

## Performance Indicators

- 🚀 **Fast**: < 1 second
- ✅ **Good**: 1-5 seconds  
- ⚠️ **Slow**: 5-15 seconds
- 🐌 **Very Slow**: > 15 seconds

## Menu Options

1. **Create new query (vim editor)**: Opens vim to create/edit YANG queries
2. **Show session statistics**: Displays cumulative statistics for current session
3. **Exit**: Closes the tool and shows final session statistics

## Session Statistics

Track performance across multiple queries:
- Total number of queries executed
- Average, minimum, and maximum query times
- Total session query time
- Per-query timing breakdown

## Error Handling

The tool provides specific error messages and troubleshooting suggestions for:

- **Connection errors**: Network connectivity, authentication issues
- **RPC errors**: Invalid YANG paths, unsupported models
- **Query errors**: Malformed XML, namespace issues

### Common Troubleshooting Steps

1. Verify YANG model support on target device
2. Check namespace URIs for accuracy
3. Test with simpler query paths
4. Confirm data exists in running configuration
5. Validate network connectivity to port 830

## Security Considerations

- **Host Key Verification**: Disabled for ease of use (consider enabling in production)
- **Credential Handling**: Passwords are masked during input but not stored
- **SSH Agent**: Disabled to use explicit password authentication

## Limitations

- Currently supports only `get-config` operations with running datastore
- Requires vim editor (modify script for alternative editors)
- Designed specifically for Cisco IOS-XE devices
- No support for edit-config or other NETCONF operations

## Development

### Key Functions

- [`get_device_credentials()`](Tools/Tools/python/query-yang.py): Handles device connection input
- [`edit_with_vim()`](Tools/Tools/python/query-yang.py): Manages vim editor integration  
- [`execute_netconf_query()`](Tools/Tools/python/query-yang.py): Performs NETCONF operations
- [`format_duration()`](Tools/Tools/python/query-yang.py): Formats timing output
- [`display_session_stats()`](Tools/Tools/python/query-yang.py): Shows session statistics

### Customization

To modify for different editors, update the `edit_with_vim()` function:
```python
subprocess.run(['nano', tmp_file_path], check=True)  # For nano
subprocess.run(['code', '--wait', tmp_file_path], check=True)  # For VS Code
```

## Example Session

```
NETCONF-YANG Query Tool for Cisco Routers
(Simplified - Always uses get-config)
=============================================

=== NETCONF Device Connection ===
Device IP Address: 192.168.1.100
Username: admin
Password: [hidden]

=== Query Options ===
1. Create new query (vim editor)
2. Show session statistics  
3. Exit

Select option (1-3): 1

[vim editor opens with example templates]

=== Connecting to 192.168.1.100 ===
✓ Connected successfully (Connection time: 1.23 seconds)

=== Sending Query ===
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/>

=== Timing Information ===
Query started:     2024-01-15 10:30:45.123
Query completed:   2024-01-15 10:30:47.456
Connection time:   1.23 seconds
Query time:        2.33 seconds
Total time:        3.56 seconds
Performance:       ✅ Good

=== Response ===
[Formatted XML response]

✓ Response saved to: netconf_response_20240115_103045.xml
```

## License

This tool is part of the troubleshooting tools repository. Please refer to the main repository license.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with detailed description

For questions or issues, please create an issue in the repository.