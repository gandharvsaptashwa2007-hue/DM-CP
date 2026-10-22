# Classroom walkthrough

Run the app locally using the README instructions. After a Git update, stop
the old process with Ctrl+C and restart it. On Windows, inside the DM-CP folder:

```bat
git pull origin main
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m streamlit run app.py
```

## 1. Link the earlier concepts

- GCD: 252 and 105 give 21, with remainders 42, 21, 0.
- Modular inverse: 17 modulo 3120 gives 2753.
- Primality: 97 is prime; 91 is composite; 561 illustrates a Fermat false positive.
- Euler's phi: 36 gives 12; the RSA modulus 3233 gives 3120.

## 2. CRT Solver

Keep the default three congruences and select **Solve system**. Walk through
each contribution, then choose **Show all steps**. The solution is 23 modulo
105. Read the verification table aloud: remainders 2, 3, 2.

Try the non-coprime preset. Explain that this version's pairwise-coprime
condition fails; the error does not claim that every such system is impossible.

## 3. RSA Lab

1. Select **Load HELLO demo**, then **Build keys**.
2. Explain: p=61, q=53, n=3233, φ(n)=3120, e=17, d=2753.
3. Open the extended-Euclid explanation to connect d to the inverse module.
4. Select **Encrypt message**. The message bytes are 72,69,76,76,79 and the
   ciphertext is 3000,28,2726,2726,1307.
5. Select **Decrypt ciphertext**. Confirm HELLO and the round-trip check.
6. Inspect one block's repeated-squaring trace. For the first block,
   `3000^2753 mod 3233 = 72`.
7. Open the CRT check. The same message has residues 11 modulo 61 and
   19 modulo 53. CRT reconstructs 72 modulo 3233.
8. Point out the repeated ciphertext for L: this byte-by-byte, unpadded RSA
   leaks patterns. It is a mathematical demonstration, not real secure messaging.

Optional checks: use a Unicode message, try integer 0 or 53, and change e to 6.
The exponent 6 is not coprime to 3120, so key generation correctly fails.
Restore the demo and encrypt again before continuing.

## 4. Break the Key

1. Select **Use RSA Lab public data**. Only the public exponent, modulus,
   ciphertext and text/integer interpretation are copied into attack inputs.
2. Select **Try to break the key**. It finds 53 and 61 in 27 candidate checks.
3. Show the recovered φ(n)=3120, d=2753, and HELLO.
4. Lower the work limit to 1 and retry: the result is unfinished, with no
   recovered private key. This limit does not establish security.
5. Restore 100,000 checks and load the larger public-key preset. Its factors
   are beyond the bounded search. Contrast the workload without treating
   these timings as predictions for modern factoring algorithms.

## Scope and handoff

All seven learning modules are present. Frontend polish, an academic report,
screenshots and any public hosting remain separate follow-up work. Core and UI
tests run with:

```bat
.venv\Scripts\python -m unittest discover -s tests -v
```
