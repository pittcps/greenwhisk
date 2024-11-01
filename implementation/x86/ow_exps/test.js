function main() {
  // Create an array of booleans representing numbers from 2 to 10,000.
  // Assume all numbers are prime initially.
  let n = 1_000_000
  let isPrime = Array(n + 1).fill(true);
  // Mark 0 and 1 as non-prime.
  isPrime[0] = false;
  isPrime[1] = false;

  // Iterate through all numbers from 2 to 10,000.
  for (let i = 2; i <= n; i++) {
    // If the current number is prime, mark all its multiples as non-prime.
    if (isPrime[i]) {
      for (let j = i * i; j <= n; j += i) {
        isPrime[j] = false;
      }
    }
  }

  // Collect all prime numbers into an array and return it.
  let primes = [];
  for (let i = 2; i <= n; i++) {
    if (isPrime[i]) {
      primes.push(i);
    }
  }
  return {"output": "done"};
}
