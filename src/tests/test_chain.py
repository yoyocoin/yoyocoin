import unittest

from blockchain import Chain
from blockchain.wallet import Wallet


class MyChainTester(unittest.TestCase):
    def setUp(self) -> None:
        Chain.reset()

    def test_epoch_random_updater_distribution(self):
        chain = Chain.get_instance()
        sample_size = 2000
        results = []
        for counter in range(sample_size):
            w = Wallet(secret_password=str(counter))
            results.append(chain._next_epoch_random(w.address))
        self.assertAlmostEqual(sum(results) / len(results), 0.5, delta=0.05)

        distribution_sections = 10
        total = 1
        distribution = [0] * distribution_sections

        for result in results:
            section_size = total / distribution_sections
            distribution[round(result / section_size) - 1] += 1

        precision = 0.3
        self.assertTrue(
            max(distribution) - min(distribution)
            < (sample_size / distribution_sections) * precision
        )


if __name__ == "__main__":
    unittest.main()
