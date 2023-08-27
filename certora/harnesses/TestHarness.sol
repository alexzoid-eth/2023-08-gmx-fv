// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

contract TestHarness {
    
    mapping(bytes32 => string) public stringValues;

    function getString(bytes32 key) external view returns (string memory) {
        return stringValues[key];
    }

    function getStringAsBytes1Array(bytes32 key) external view returns (bytes1[] memory) {

        bytes memory barr = bytes(this.getString(key)); 
        bytes1[] memory arr = new bytes1[](barr.length);  

        for (uint256 i; i < barr.length; ++i) {
            arr[i] = bytes1(barr[i]);
        }

        return arr;
    }
}
