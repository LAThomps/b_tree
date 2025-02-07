import numpy as np
import time

start = time.time()
rand = np.random.default_rng()

with open("../b_tree_files/vals.txt", "w") as file:
    for i in range(30):
        print(i + 1)
        nums = rand.integers(100000, 2000000, 50000000)
        nums.tofile(file, sep="\n")
    print()

end = time.time()
print(f"complete, {end - start:.2f} seconds elapsed")