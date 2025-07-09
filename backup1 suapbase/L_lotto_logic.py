import random
from collections import Counter
from typing import List, Optional, Callable, Dict, Any, Set, Tuple

class LottoLogic:
    MIN_NUM: int = 1
    MAX_NUM: int = 45
    NUM_BALLS: int = 6

    def __init__(self, past_winnings: Optional[List[List[int]]] = None) -> None:
        self.past_winnings = past_winnings if past_winnings is not None else []
        self._patterns_analyzed = False
        
        # Initialize properties
        self.number_freq: Counter = Counter()
        self.hot_numbers: List[int] = []
        self.cold_numbers: List[int] = []
        self.pair_freq: Counter = Counter()
        self.incompatible_pairs: Set[Tuple[int, int]] = set()
        self.long_term_unseen: List[int] = []
        self.sum_stats: Dict[str, float] = {'min': 0, 'max': 0, 'avg': 0}

        if self.past_winnings:
            self._analyze_patterns()

    def _analyze_patterns(self) -> None:
        if self._patterns_analyzed:
            return
        
        if not self.past_winnings:
            return
            
        # Use list comprehensions for better performance
        all_numbers_flat = [num for game in self.past_winnings for num in game]
        sums = [sum(game) for game in self.past_winnings]
        
        # Clear and rebuild pair frequency counter
        self.pair_freq.clear()
        for game in self.past_winnings:
            # Generate pairs more efficiently
            for i in range(self.NUM_BALLS):
                for j in range(i + 1, self.NUM_BALLS):
                    pair = tuple(sorted((game[i], game[j])))
                    self.pair_freq[pair] += 1
        
        if not all_numbers_flat:
            return

        self.number_freq = Counter(all_numbers_flat)
        total_freq = sum(self.number_freq.values())
        unique_numbers = len(self.number_freq)
        
        if unique_numbers > 0:
            avg_freq = total_freq / unique_numbers
            
            # Use more efficient filtering
            hot_items = [(n, f) for n, f in self.number_freq.items() if f > avg_freq]
            self.hot_numbers = [n for n, f in sorted(hot_items, key=lambda x: x[1], reverse=True)]
            
            all_numbers = set(range(self.MIN_NUM, self.MAX_NUM + 1))
            cold_numbers = [(n, self.number_freq.get(n, 0)) for n in all_numbers if self.number_freq.get(n, 0) < avg_freq]
            self.cold_numbers = [n for n, f in sorted(cold_numbers, key=lambda x: x[1])]
        
        # Only keep pairs that appear very rarely
        self.incompatible_pairs = {p for p, f in self.pair_freq.items() if f <= 1}
        
        # Use set operations for better performance
        recent_limit = min(15, len(self.past_winnings))
        recent_numbers = set()
        for game in self.past_winnings[-recent_limit:]:
            recent_numbers.update(game)
        
        self.long_term_unseen = [n for n in range(self.MIN_NUM, self.MAX_NUM + 1) if n not in recent_numbers]
        
        if sums:
            self.sum_stats = {'min': min(sums), 'max': max(sums), 'avg': sum(sums) / len(sums)}
        
        self._patterns_analyzed = True

    def _generate_with_filter(self, condition: Callable[[List[int]], bool], max_trials: int = 100) -> List[int]:
        """Helper to generate numbers satisfying a condition."""
        for _ in range(max_trials):
            numbers = sorted(random.sample(range(self.MIN_NUM, self.MAX_NUM + 1), self.NUM_BALLS))
            if condition(numbers):
                return numbers
        return self.generate_random()

    def generate_random(self) -> List[int]: 
        return sorted(random.sample(range(self.MIN_NUM, self.MAX_NUM + 1), self.NUM_BALLS))

    def generate_pattern(self) -> List[int]: 
        if not self.past_winnings:
            return self.generate_random()
        population = list(self.number_freq.keys())
        weights = list(self.number_freq.values())
        if not population:
            return self.generate_random()
        
        numbers = set()
        max_attempts = 100
        attempt = 0
        while len(numbers) < self.NUM_BALLS and attempt < max_attempts: 
            numbers.add(random.choices(population, weights=weights, k=1)[0])
            attempt += 1
        return sorted(list(numbers))

    def generate_inverse_pattern(self) -> List[int]:
        if not self.past_winnings:
            return self.generate_random()
        all_possible_nums = list(range(self.MIN_NUM, self.MAX_NUM + 1))
        max_f = max(self.number_freq.values()) if self.number_freq else 0
        weights = [(max_f - self.number_freq.get(num, 0)) + 1 for num in all_possible_nums]
        
        numbers = set()
        max_attempts = 100
        attempt = 0
        while len(numbers) < self.NUM_BALLS and attempt < max_attempts:
            numbers.add(random.choices(all_possible_nums, weights=weights, k=1)[0])
            attempt += 1
        return sorted(list(numbers))

    def generate_balance(self) -> List[int]:
        return self._generate_with_filter(lambda n: 2 <= sum(1 for x in n if x % 2 == 0) <= 4)

    def generate_range_distribution(self) -> List[int]:
        try:
            n = set()
            ranges = [(1, 15), (16, 30), (31, 45)]
            for s, e in ranges:
                n.update(random.sample(range(s, e + 1), 2))
            while len(n) < self.NUM_BALLS:
                n.add(random.randint(self.MIN_NUM, self.MAX_NUM))
            # Ensure we don't try to sample more than available
            sample_size = min(self.NUM_BALLS, len(n))
            return sorted(random.sample(list(n), sample_size))
        except (ValueError, IndexError): 
            return self.generate_random()

    def generate_prime(self) -> List[int]:
        primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43}
        return self._generate_with_filter(lambda n: sum(1 for x in n if x in primes) >= 2)

    def generate_sum_range(self, min_sum: Optional[int] = None, max_sum: Optional[int] = None) -> List[int]:
        min_s = min_sum or (self.sum_stats['min'] if self.past_winnings else 111)
        max_s = max_sum or (self.sum_stats['max'] if self.past_winnings else 170)
        return self._generate_with_filter(lambda n: min_s <= sum(n) <= max_s)

    def generate_consecutive(self) -> List[int]:
        def has_consecutive(n: List[int]) -> bool:
            for i in range(len(n) - 1):
                if n[i+1] == n[i] + 1:
                    return True
            return False
        return self._generate_with_filter(has_consecutive)

    def generate_hot_cold_mix(self) -> List[int]:
        if not self.past_winnings:
            return self.generate_random()
        
        n = set()
        if self.hot_numbers: 
            n.update(random.sample(self.hot_numbers, min(3, len(self.hot_numbers))))
        if self.cold_numbers: 
            n.update(random.sample(self.cold_numbers, min(3, len(self.cold_numbers))))
        
        while len(n) < self.NUM_BALLS: 
            n.add(random.randint(self.MIN_NUM, self.MAX_NUM))
        # Ensure we don't try to sample more than available
        sample_size = min(self.NUM_BALLS, len(n))
        return sorted(random.sample(list(n), sample_size))

    def generate_frequent_pairs(self) -> List[int]:
        if not self.pair_freq:
            return self.generate_random()
        
        top_pairs = self.pair_freq.most_common(10)
        if not top_pairs:
            return self.generate_random()

        n = set(random.choice(top_pairs)[0])
        while len(n) < self.NUM_BALLS: 
            n.add(random.randint(self.MIN_NUM, self.MAX_NUM))
        # Ensure we don't try to sample more than available
        sample_size = min(self.NUM_BALLS, len(n))
        return sorted(random.sample(list(n), sample_size))

    def generate_ending_pattern(self) -> List[int]:
        groups = {i: [n for n in range(self.MIN_NUM, self.MAX_NUM + 1) if n % 10 == i] for i in range(10)}
        n = set()
        # Pick 1 to 3 numbers from a random ending group
        for _ in range(random.randint(1, 3)): 
            chosen_ending = random.choice(list(groups.keys()))
            if groups[chosen_ending]: 
                n.add(random.choice(groups[chosen_ending]))
        
        while len(n) < self.NUM_BALLS: 
            n.add(random.randint(self.MIN_NUM, self.MAX_NUM))
        # Ensure we don't try to sample more than available
        sample_size = min(self.NUM_BALLS, len(n))
        return sorted(random.sample(list(n), sample_size))

    def generate_statistical_optimal(self) -> List[int]:
        if not self.past_winnings:
            return self.generate_random()
        
        min_s, max_s = self.sum_stats['min'], self.sum_stats['max']
        
        def is_optimal(n: List[int]) -> bool:
            s = sum(n)
            even_count = sum(1 for x in n if x % 2 == 0)
            return (2 <= even_count <= 4) and (min_s <= s <= max_s)

        return self._generate_with_filter(is_optimal, max_trials=200)

    def generate_carryover_unseen_mix(self) -> List[int]:
        if len(self.past_winnings) < 15:
            return self.generate_random()
        
        n = set(random.sample(self.past_winnings[-1], random.randint(1, 2)))
        if self.long_term_unseen: 
            n.update(random.sample(self.long_term_unseen, random.randint(2, 3)))
        
        while len(n) < self.NUM_BALLS: 
            n.add(random.randint(self.MIN_NUM, self.MAX_NUM))
        # Ensure we don't try to sample more than available
        sample_size = min(self.NUM_BALLS, len(n))
        return sorted(random.sample(list(n), sample_size))

    def generate_same_ending_mix(self) -> List[int]:
        groups = {i: [n for n in range(self.MIN_NUM, self.MAX_NUM + 1) if n % 10 == i] for i in range(10)}
        endings_with_pairs = [i for i, g in groups.items() if len(g) >= 2]
        if not endings_with_pairs:
            return self.generate_random()
        
        chosen_ending = random.choice(endings_with_pairs)
        n = set(random.sample(groups[chosen_ending], 2))
        
        while len(n) < self.NUM_BALLS: 
            n.add(random.randint(self.MIN_NUM, self.MAX_NUM))
        return sorted(list(n))

    def generate_compatibility_mix(self) -> List[int]:
        if not self.incompatible_pairs:
            return self.generate_random()

        def is_compatible(n: List[int]) -> bool:
            for i in range(self.NUM_BALLS):
                for j in range(i + 1, self.NUM_BALLS):
                    if tuple(sorted((n[i], n[j]))) in self.incompatible_pairs:
                        return False
            return True
        
        return self._generate_with_filter(is_compatible, max_trials=200)

    def _get_generation_methods(self, data_driven_only: bool = False, all_methods: bool = False) -> List[Callable[[], List[int]]]:
        """Helper to get a list of generation methods."""
        # All methods are stored with a boolean indicating if they depend on past data
        all_method_map = [
            (self.generate_random, False),
            (self.generate_pattern, True),
            (self.generate_inverse_pattern, True),
            (self.generate_balance, False),
            (self.generate_range_distribution, False),
            (self.generate_prime, False),
            (self.generate_sum_range, True),
            (self.generate_consecutive, False),
            (self.generate_hot_cold_mix, True),
            (self.generate_frequent_pairs, True),
            (self.generate_ending_pattern, False), # Doesn't strictly need past data
            (self.generate_statistical_optimal, True),
            (self.generate_carryover_unseen_mix, True),
            (self.generate_same_ending_mix, False), # Doesn't strictly need past data
            (self.generate_compatibility_mix, True),
        ]
        
        if data_driven_only:
            return [m for m, is_data_dep in all_method_map if is_data_dep]
        if all_methods:
            return [m for m, _ in all_method_map]
        return [m for m, _ in all_method_map]


    def generate_data_driven_mix(self) -> List[int]:
        if not self.past_winnings:
            return self.generate_random()
        
        methods = self._get_generation_methods(data_driven_only=True)
        all_n = set()
        for method in methods:
            try:
                all_n.update(method())
            except Exception:
                continue # Ignore errors in sub-methods
        
        while len(all_n) < self.NUM_BALLS: 
            all_n.add(random.randint(self.MIN_NUM, self.MAX_NUM))
        # Ensure we don't try to sample more than available
        sample_size = min(self.NUM_BALLS, len(all_n))
        return sorted(random.sample(list(all_n), sample_size))

    def generate_all_methods(self) -> List[int]:
        methods = self._get_generation_methods(all_methods=True)
        all_n = set()
        
        for method in methods:
            try: 
                all_n.update(method())
            except Exception: 
                continue
        
        while len(all_n) < self.NUM_BALLS: 
            all_n.add(random.randint(self.MIN_NUM, self.MAX_NUM))
        # Ensure we don't try to sample more than available
        sample_size = min(self.NUM_BALLS, len(all_n))
        return sorted(random.sample(list(all_n), sample_size))
