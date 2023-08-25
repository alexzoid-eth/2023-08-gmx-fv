pragma solidity 0.8.19;

library Role {
    bytes32 public constant NAME_1 = keccak256(abi.encode("NAME_1"));
    bytes32 public constant NAME_2 = keccak256(abi.encode("NAME_2"));
}

contract TestHarness {

    bytes32 public owner;

    constructor() {
        owner = Role.NAME_1;
    }

    function name1() external pure returns (bytes32) {
        return Role.NAME_1;
    }

    function name2() external pure returns (bytes32) {
        return Role.NAME_2;
    }
}
