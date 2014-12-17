{
    'scene': 'poppy-flying.ttt',

    'bab': 'goal',
    'im': {'name': 'random', 'conf': {}},
    'sm': {'name': 'knn', 'conf': {'sigma_ratio': 1 / 6.}},

    'eval_at': [5, 10, 20, 30, 40, 50, 100, 150,
                200, 250, 300, 400, 500, 600, 700, 800, 900, 1000,
                1250, 1500, 1750, 2000, 3000, 4000, 5000],
    'tc': 'tc-150.npy',

    'log_folder': 'logs/gridsearch',
    'log': 'rg-knn-default',
}
