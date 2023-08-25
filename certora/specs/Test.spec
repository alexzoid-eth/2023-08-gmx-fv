using Role as _Role;

methods {
    function owner() internal returns (bytes32);
    function name1() external returns (bytes32) envfree;
    function name2() external returns (bytes32) envfree;
}

invariant ownerSetupInConstructor(env e) true {
    preserved {
        assert(owner(e) != _Role.NAME_1(e));
    }
}

rule test(env e) {
    assert(_Role.NAME_1(e) != name2());
}