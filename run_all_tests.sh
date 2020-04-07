# test given levels
for level in {1..4}
do
    time python -m search "search/test_cases/test-level-$level.json" "expendi_search" 2> search/test_results/stderr-expendi-level-${level}.txt

    # time python -m search "search/test_cases/test-level-$level.json" "depth_first_search" 2> search/test_results/stderr-depth-first-level-${level}.txt

    # time python -m search "search/test_cases/test-level-$level.json" "breadth_first_search" 2> search/test_results/stderr-breadth-first-level-${level}.txt
done


# test custom levels
for level in {0..19}
do
    time python -m search "search/custom_test_cases/test-level-$level.json" "expendi_search" 2> search/test_results/stderr-expendi-level-C${level}.txt

    # time python -m search "search/custom_test_cases/test-level-$level.json" "depth_first_search" 2> search/test_results/stderr-depth-first-level-C${level}.txt

    # time python -m search "search/custom_test_cases/test-level-$level.json" "breadth_first_search" 2> search/test_results/stderr-breadth-first-level-C${level}.txt
done