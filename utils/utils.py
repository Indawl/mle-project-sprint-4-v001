import pandas as pd

from implicit.als import AlternatingLeastSquares


items = pd.read_parquet('recsys/data/items.parquet')

als_model = AlternatingLeastSquares(factors=50, iterations=50, regularization=0.05, random_state=0)
als_model = als_model.load("recsys/models/als_model.npz")


async def als_sim(item_id: int, N: int = 1):
    """
    Поиск похожих треков через ALS
    """
        
    item = items.loc[items["item_id"] == item_id]
    if item.empty:
        return [], []
    
    item_id_enc = item["item_id_enc"].iloc[0]
    similar_items = als_model.similar_items(item_id_enc, N=N)
    enc_ids, scores = similar_items[0][1:N+1], similar_items[1][1:N+1]

    similar_tracks = items[items["item_id_enc"].isin(enc_ids)]["item_id"].tolist()
    return similar_tracks, scores
