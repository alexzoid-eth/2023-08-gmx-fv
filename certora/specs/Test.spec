methods {
    function getStringAsBytes1Array(bytes32) external returns (bytes1[]) envfree;
}

ghost mapping(bytes32 => mapping(uint256 => bytes1)) ghostStringValues {
    init_state axiom forall bytes32 key. forall uint256 index. ghostStringValues[key][index] == to_bytes1(0);
}

hook Sstore currentContract.stringValues[KEY bytes32 key][INDEX uint256 index] bytes1 val STORAGE {
    ghostStringValues[key][index] = val;
}

hook Sload bytes1 val currentContract.stringValues[KEY bytes32 key][INDEX uint256 index] STORAGE {
    require(ghostStringValues[key][index] == val);
}

rule getStringIntegrity(bytes32 key) { 

    bytes1[] a = getStringAsBytes1Array(key);

    uint256 i;
    require(i < a.length);

    assert(a[i] == ghostStringValues[key][i]); 
}
