using DummyERC20A as _DummyERC20A;

///////////////// METHODS //////////////////////

methods {

    // Harness envfree
    function isController(address) external returns (bool) envfree;
    function wntAddress() external returns (address) envfree;

    // Harness
    function afterTransferOut(address) external;

    // Bank
    function transferOut(address, address, uint256, bool) external;
    function transferOutNativeToken(address, uint256) external;

    // ERC20
    function _.name() external  => DISPATCHER(true);
    function _.symbol() external  => DISPATCHER(true);
    function _.decimals() external  => DISPATCHER(true);
    function _.totalSupply() external  => DISPATCHER(true);
    function _.balanceOf(address) external  => DISPATCHER(true);
    function _.allowance(address,address) external  => DISPATCHER(true);
    function _.approve(address,uint256) external  => DISPATCHER(true);
    function _.transfer(address,uint256) external  => DISPATCHER(true);
    function _.transferFrom(address,address,uint256) external  => DISPATCHER(true);

    // DataStore
    function _.getUint(bytes32) external => DISPATCHER(true);
    function _.getAddress(bytes32) external => DISPATCHER(true);
    function _.getBytes32(bytes32) external => DISPATCHER(true);

    // RoleStore
    function _.hasRole(address,bytes32) external => DISPATCHER(true);

    // WNT
    function _.deposit() external  => DISPATCHER(true);
    function _.withdraw(uint256) external  => DISPATCHER(true);

    function tokenBalances(address) external returns (uint256) envfree;
}

///////////////// DEFINITIONS /////////////////////

definition PURE_VIEW_FUNCTIONS(method f) returns bool = f.isView || f.isPure;
definition FALLBACK_FUNCTIONS(method f) returns bool = f.isFallback;

definition HARNESS_FUNCTIONS(method f) returns bool = 
    f.selector == sig:afterTransferOut(address).selector
    || f.selector == sig:isController(address).selector;

////////////////// FUNCTIONS //////////////////////

function setupEssential(env e) {
    require e.msg.value == 0;
    require e.block.number != 0;
}

///////////////// GHOSTS & HOOKS //////////////////

// Ghost copy of tokenBalances[]

ghost mapping(address => uint256) ghostTokenBalancesPrev {
    init_state axiom forall address token. ghostTokenBalancesPrev[token] == 0;
}

ghost mapping(address => uint256) ghostTokenBalances {
    init_state axiom forall address token. ghostTokenBalances[token] == 0;
}

hook Sstore tokenBalances[KEY address token] uint256 balance (uint256 prevBalance) STORAGE {
    ghostTokenBalancesPrev[token] = prevBalance;
    ghostTokenBalances[token] = balance;
}

hook Sload uint256 balance tokenBalances[KEY address token] STORAGE {
    require ghostTokenBalances[token] == balance;
}

// Ghost copy of _DummyERC20A.balances[]

ghost mapping(address => uint256) ghostDummyERC20ABalances {
    init_state axiom forall address account. ghostDummyERC20ABalances[account] == 0;
}

hook Sstore _DummyERC20A.balances[KEY address account] uint256 balance STORAGE {
    ghostDummyERC20ABalances[account] = balance;
}

hook Sload uint256 balance _DummyERC20A.balances[KEY address account] STORAGE {
    require ghostDummyERC20ABalances[account] == balance;
}

///////////////// PROPERTIES //////////////////////

// [1-3] `tokenBalances` storage variable should be equal to balance of current contract 
invariant tokenBalancesSolvency() ghostTokenBalances[_DummyERC20A] == ghostDummyERC20ABalances[currentContract] filtered { 
    f -> !PURE_VIEW_FUNCTIONS(f) && !HARNESS_FUNCTIONS(f) 
}

// [4] interaction with a token should not change balance of another token
rule balanceIndependence(method f, env e, address token1, address token2) filtered {
    f -> f.selector == sig:recordTransferIn(address).selector 
        || f.selector == sig:afterTransferOut(address).selector
        || f.selector == sig:syncTokenBalance(address).selector
} {
    uint256 balanceBefore = tokenBalances(token2);

    if (f.selector == sig:recordTransferIn(address).selector) {
        recordTransferIn(e, token1);
    } else if (f.selector == sig:afterTransferOut(address).selector) {
        afterTransferOut(e, token1);
    } else if (f.selector == sig:syncTokenBalance(address).selector) {
        syncTokenBalance(e, token1);
    }

    uint256 balanceAfter = tokenBalances(e, token2); 

    assert(token2 != token1 => balanceBefore == balanceAfter);
} 

// [5-9] onlyController can execute non-view functions, otherwise got reverted
rule onlyControllerCouldChangeState(env e, method f, calldataarg args) filtered { 
    f -> !PURE_VIEW_FUNCTIONS(f) && !FALLBACK_FUNCTIONS(f) && !HARNESS_FUNCTIONS(f) 
} {

    bool controller = isController(e.msg.sender);

    storage before = lastStorage;

    f@withrevert(e, args);
    bool reverted = lastReverted;

    storage after = lastStorage;

    assert(!controller => reverted);
    assert(!reverted && before[currentContract] != after[currentContract] => controller);
}

// [10] recordTransferIn() should update token balance in a big way 
invariant recordTransferInTokenBalanceGreater(address token) ghostTokenBalances[token] >= ghostTokenBalancesPrev[token]
    filtered { f -> f.selector == sig:recordTransferIn(address).selector }

// [11-12] receive native tokens only via payable fallback and from `wnt` contract

ghost bool sentNativeTokensToStrictBankFallback;
hook CALL(uint256 g, address addr, uint256 value, uint256 argsOffset, uint256 argsLength, uint256 retOffset, uint256 retLength) uint256 rc {
    sentNativeTokensToStrictBankFallback = sentNativeTokensToStrictBankFallback == false // set variable once
        ? rc != 0 // call status success
            && addr == currentContract // send to currentContract
            && value != 0 // native tokens
            && argsLength == 0 // send to fallback
        : sentNativeTokensToStrictBankFallback;
}

rule receiveNativeTokensViaFallbackFromWnt(env e, method f, calldataarg args) filtered { 
    f -> !PURE_VIEW_FUNCTIONS(f) && !HARNESS_FUNCTIONS(f) 
} {
    require sentNativeTokensToStrictBankFallback == false;

    mathint balanceBefore = nativeBalances[currentContract];

    f(e, args);

    mathint balanceAfter = nativeBalances[currentContract];

    assert(balanceAfter > balanceBefore => FALLBACK_FUNCTIONS(f) && e.msg.sender == wntAddress() || sentNativeTokensToStrictBankFallback);
}

// [13] possibility of receiving native tokens via fallback from `wnt` address
rule receiveNativeTokensInFallbackFromWntPossibility(env e, method f, calldataarg args) filtered { 
    f -> FALLBACK_FUNCTIONS(f) 
} {
    require e.msg.sender == wntAddress();

    mathint balanceBefore = nativeBalances[currentContract];

    f(e, args);

    mathint balanceAfter = nativeBalances[currentContract];

    satisfy(balanceAfter > balanceBefore);
}