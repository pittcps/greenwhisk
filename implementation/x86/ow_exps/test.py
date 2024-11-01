def main(args):
    # Create a list of booleans representing numbers from 2 to n
    # Assume all numbers are prime initially.
    n = 1_000_000

    is_prime = [True] * (n + 1)
    # Mark 0 and 1 as non-prime.
    is_prime[0] = False
    is_prime[1] = False

    # Iterate through all numbers from 2 to 1,000,000.
    for i in range(2, n + 1):
        # If the current number is prime, mark all its multiples as non-prime.
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False

    # Collect all prime numbers into a list and return it.
    primes = []
    for i in range(2, n + 1):
        if is_prime[i]:
            primes.append(i)

    return {"output": "done"}
