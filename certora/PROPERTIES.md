# StrictBank

## High-Level
- [5-9] onlyController can execute non-view functions, otherwise got reverted
    - `onlyControllerCouldChangeState`
- [4] interaction with a token should not change balance of another token
    - `balanceIndependence`
- [15-18] transfer out should correctly update all balances
## Valid States
- [1-3] tokenBalances storage variable should be equal to balance of current contract  
    - `tokenBalancesSolvency`
## State Transitions
- [11-12] receive native tokens only via payable fallback and from `wnt` contract
    - `receiveNativeTokensFromWnt`
## Variable Transitions
- [10] recordTransferIn() should update token balance in a big way
    - `recordTransferInTokenBalanceGreater`
## Unit Tests
- [13-14] transfer out to the current contract is forbidden
    - `transferOutToCurrentContractForbidden`
- [19] syncTokenBalance() integrity
    - `syncTokenBalanceIntegrity`
- [20] recordTransferIn() integrity
    - `recordTransferInIntegrity`