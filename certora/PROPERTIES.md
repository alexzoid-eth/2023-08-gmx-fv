# StrictBank

## High-Level
- [5-9] onlyController can execute non-view functions, otherwise got reverted
    - `onlyControllerCouldChangeState`
- [4] interaction with a token should not change balance of another token
    - `balanceIndependence`

## Valid States
- [1-3] tokenBalances storage variable should be equal to balance of current contract  
    - `tokenBalancesSolvency`

## State Transitions
- [11-12] receive native tokens only via payable fallback and from `wnt` contract
    - `receiveNativeTokensViaFallbackFromWnt`
- [13] possibility of receiving native tokens via fallback from `wnt` address
    - `receiveNativeTokensInFallbackFromWntPossibility`

## Variable Transitions
- [10] `recordTransferIn()` should update token balance in a big way
    - `recordTransferInTokenBalanceGreater`

## Unit Tests
- should not revert
- correct return values