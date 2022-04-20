import pytest

from brownie import ZERO_ADDRESS

from support.constants import ADMIN_DELAY, AddressProviderKeys


@pytest.fixture
def curveInitialLiquidity(curveCoins, curveSwap, admin, coin):
    # mint 100,000 of each coin and add as initial liquidity
    amounts = []
    for coin in curveCoins:
        decimals = coin.decimals()
        initial_amount = 10**decimals * 100000
        coin.mint_for_testing(admin, initial_amount, {"from": admin})
        coin.approve(curveSwap, initial_amount, {"from": admin})
        amounts.append(initial_amount)
    curveSwap.add_liquidity(amounts, 0, {"from": admin})


@pytest.fixture
def initialAmounts(curveCoins):
    amounts = []
    for coin in curveCoins:
        decimals = coin.decimals()
        amount = 10**decimals * 100000
        amounts.append(amount)
    return amounts


@pytest.fixture
def curveSetUp(
    admin, curveSwap, curveInitialLiquidity, curveCoins, initialAmounts, alice
):
    for coin, amount in zip(curveCoins, initialAmounts):
        coin.mint_for_testing(alice, amount, {"from": admin})
        coin.approve(curveSwap, amount, {"from": alice})


@pytest.fixture
def approveAlice(coin, pool, alice):
    coin.approve(pool, 2**256 - 1, {"from": alice})


@pytest.fixture
def approveBob(coin, pool, bob):
    coin.approve(pool, 2**256 - 1, {"from": bob})


@pytest.fixture
def initialAmount(coin, decimals):
    if coin != ZERO_ADDRESS:
        # 1e6 initial amount
        return 1000000 * 10**decimals
    else:
        # coin is ETH
        return 100 * 10**decimals


@pytest.fixture
def mintAlice(admin, alice, coin, initialAmount):
    coin.mint_for_testing(alice, initialAmount, {"from": admin})


@pytest.fixture
def mintBob(admin, bob, coin, initialAmount):
    coin.mint_for_testing(bob, initialAmount, {"from": admin})


def _mint(account, amount, token, admin):
    token.mint_for_testing(account, amount, {"from": admin})


def _addInitialLiquidity(admin, account, lpToken, coin, pool, amount):
    if coin == ZERO_ADDRESS:
        tx = pool.deposit(amount, {"value": amount, "from": admin})
    else:
        coin.mint_for_testing(admin, amount, {"from": admin})
        coin.approve(pool, amount, {"from": admin})
        tx = pool.deposit(amount, {"from": admin})
    lpToken.transfer(account, tx.return_value, {"from": admin})


@pytest.fixture
def addInitialLiquidity(admin, alice, lpToken, coin, pool, initialAmount):
    _addInitialLiquidity(admin, alice, lpToken, coin, pool, initialAmount)


@pytest.fixture
def addInitialLiquidityTopUpAction(
    admin, topUpAction, lpToken, coin, pool, initialAmount
):
    _addInitialLiquidity(admin, topUpAction, lpToken, coin, pool, initialAmount)


# only for testing LP Token contract - do not use with liquidity pools
# as this will break the exchange rate
@pytest.fixture
def mintLpAlice(alice, lpToken, initialAmount, admin):
    _mint(alice, initialAmount, lpToken, admin)


@pytest.fixture
def set_bkd_locker_to_mock_token(address_provider, mockToken, admin):
    address_provider.initializeAndFreezeAddress(
        AddressProviderKeys.BKD_LOCKER.value, mockToken, {"from": admin}
    )


@pytest.fixture
def execute_with_delay(chain, admin):
    def _execute_with_delay(contract, key: str, *args):
        key = key[0].upper() + key[1:]
        prepare = getattr(contract, f"prepare{key}")
        prepare(*args, {"from": admin})
        chain.sleep(ADMIN_DELAY)
        execute = getattr(contract, f"execute{key}")
        return execute({"from": admin})

    return _execute_with_delay
