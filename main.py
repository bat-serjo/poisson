
import io
import time
import base64
import asyncio
import tornado
import tornado.web
import tornado.escape
import tornado.concurrent


class MainHandler(tornado.web.RequestHandler):
    executor = tornado.concurrent.futures.ThreadPoolExecutor(64)

    @tornado.concurrent.run_on_executor
    def post(self):
        req = tornado.escape.json_decode(self.request.body)
        ret = poisson(base64.b64decode(req['data']).decode())
        self.write(base64.b64encode(ret.encode()))


def poisson(data: str):
    import numpy as np
    from patsy import dmatrices
    import pandas as pd
    import statsmodels.api as sm

    # make sure you put the correct column index that holds the timestamp here
    date_col = [1]
    df = pd.read_csv(io.StringIO(data), delimiter=",",
                     index_col=date_col, parse_dates=date_col, date_format="%m/%d/%Y %H:%M")

    # make test data
    ds = df.index.to_series()
    df["DAY_OF_WEEK"] = ds.dt.day_of_week
    df["HOUR"] = ds.dt.hour
    df["MINUTE"] = ds.dt.minute

    # # make an 80% mask (pick 80% of input data as train use 20% as test)
    # mask = np.random.rand(len(df)) < 0.8
    # df_train = df[mask]
    # df_test = df[~mask]
    # print('Training data set length=' + str(len(df_train)))
    # print('Testing data set length=' + str(len(df_test)))

    df_train = df

    expr = """id ~ DAY_OF_WEEK + HOUR + MINUTE"""
    y_train, x_train = dmatrices(expr, df_train, return_type='dataframe')
    # y_test, x_test = dmatrices(expr, df_test, return_type='dataframe')

    trained_model = sm.GLM(y_train, x_train, family=sm.families.Poisson()).fit()
    # print(trained_model.summary())

    predictions = trained_model.get_prediction(x_train)
    frame = predictions.summary_frame()
    # print(frame)
    return str(frame)


async def main():
    # d = "aWQsZGF0ZQoyNzk0ODk5OSwxMS8xLzIwMjMgMTE6MDUKMjc5NDg1ODEsMTEvMS8yMDIzIDExOjAxCjI3OTQ4NTkwLDExLzEvMjAyMyAxMTowMQoyNzk0OTY0OSwxMS8xLzIwMjMgMTE6MTIKMjc5NDk4MDAsMTEvMS8yMDIzIDExOjEzCjI3OTQ5MjYxLDExLzEvMjAyMyAxMTowOAoyNzk0OTA1NCwxMS8xLzIwMjMgMTE6MDUKMjc5NDk1OTYsMTEvMS8yMDIzIDExOjExCjI3OTQ5NTA4LDExLzEvMjAyMyAxMToxMAoyNzk0OTkxNiwxMS8xLzIwMjMgMTE6MTQKMjc5NDk2NjgsMTEvMS8yMDIzIDExOjEyCjI3OTQ4NDc5LDExLzEvMjAyMyAxMTowMAoyNzk1MDM4NSwxMS8xLzIwMjMgMTE6MTgKMjc5NDg2NDQsMTEvMS8yMDIzIDExOjAxCjI3OTUwODc3LDExLzEvMjAyMyAxMToyNQoyNzk0OTY2MSwxMS8xLzIwMjMgMTE6MTIKMjc5NTAxMDcsMTEvMS8yMDIzIDExOjE1CjI3OTQ5NzYxLDExLzEvMjAyMyAxMToxMwoyNzk0OTc2NywxMS8xLzIwMjMgMTE6MTMKMjc5NTA2ODMsMTEvMS8yMDIzIDExOjIyCjI3OTQ4ODk4LDExLzEvMjAyMyAxMTowMwoyNzk0ODU3NywxMS8xLzIwMjMgMTE6MDEKMjc5NDk5NTYsMTEvMS8yMDIzIDExOjE0CjI3OTQ5MzU5LDExLzEvMjAyMyAxMTowOQoyNzk1MDI3NywxMS8xLzIwMjMgMTE6MTcKMjc5NDg5MzUsMTEvMS8yMDIzIDExOjA0CjI3OTQ5NDczLDExLzEvMjAyMyAxMToxMAoyNzk0OTgxMiwxMS8xLzIwMjMgMTE6MTMKMjc5NTE0MDEsMTEvMS8yMDIzIDExOjMwCjI3OTUwNDU3LDExLzEvMjAyMyAxMToxOQoyNzk0OTYzOSwxMS8xLzIwMjMgMTE6MTIKMjc5NDk3MjksMTEvMS8yMDIzIDExOjEzCjI3OTUwMzI1LDExLzEvMjAyMyAxMToxOAoyNzk1MDczOSwxMS8xLzIwMjMgMTE6MjIKMjc5NTEyMjksMTEvMS8yMDIzIDExOjI5CjI3OTUwOTE4LDExLzEvMjAyMyAxMToyNQoyNzk0OTIyMCwxMS8xLzIwMjMgMTE6MDcKMjc5NTEyODMsMTEvMS8yMDIzIDExOjI5CjI3OTUxODYxLDExLzEvMjAyMyAxMTozNAoyNzk0OTYyMiwxMS8xLzIwMjMgMTE6MTEKMjc5NTAxNjUsMTEvMS8yMDIzIDExOjE2CjI3OTUxNTQwLDExLzEvMjAyMyAxMTozMQoyNzk1MDQ4NiwxMS8xLzIwMjMgMTE6MTkKMjc5NTE5MDEsMTEvMS8yMDIzIDExOjM1CjI3OTUwNjI0LDExLzEvMjAyMyAxMToyMQoyNzk1MDg0MSwxMS8xLzIwMjMgMTE6MjQKMjc5NTE2OTIsMTEvMS8yMDIzIDExOjMyCjI3OTUyOTMyLDExLzEvMjAyMyAxMTo0NQoyNzk1MTU3MywxMS8xLzIwMjMgMTE6MzEKMjc5NTE4MzcsMTEvMS8yMDIzIDExOjM0CjI3OTUwMzI0LDExLzEvMjAyMyAxMToxOAoyNzk1MTE0NSwxMS8xLzIwMjMgMTE6MjgKMjc5NTE1NjcsMTEvMS8yMDIzIDExOjMxCjI3OTUyNTQ5LDExLzEvMjAyMyAxMTo0MQoyNzk1MzE1MywxMS8xLzIwMjMgMTE6NDgKMjc5NTMyMDMsMTEvMS8yMDIzIDExOjQ4CjI3OTUxNDA5LDExLzEvMjAyMyAxMTozMAoyNzk1Mjg5MSwxMS8xLzIwMjMgMTE6NDUKMjc5NTI4NDUsMTEvMS8yMDIzIDExOjQ0CjI3OTUzMDI3LDExLzEvMjAyMyAxMTo0NgoyNzk1MzMzMCwxMS8xLzIwMjMgMTE6NDkKMjc5NTMzMzUsMTEvMS8yMDIzIDExOjQ5CjI3OTUyNzE0LDExLzEvMjAyMyAxMTo0MwoyNzk1MjQ5MCwxMS8xLzIwMjMgMTE6NDEKMjc5NTIxODEsMTEvMS8yMDIzIDExOjM3CjI3OTUzNzg2LDExLzEvMjAyMyAxMTo1NAoyNzk1Mzc4MiwxMS8xLzIwMjMgMTE6NTQKMjc5NTM3OTQsMTEvMS8yMDIzIDExOjU0CjI3OTUzODgwLDExLzEvMjAyMyAxMTo1NQoyNzk1MzI4MSwxMS8xLzIwMjMgMTE6NDkKMjc5NTI4NjgsMTEvMS8yMDIzIDExOjQ1CjI3OTUzODA3LDExLzEvMjAyMyAxMTo1NAoyNzk1Mzk1MywxMS8xLzIwMjMgMTE6NTYKMjc5NTI5MjgsMTEvMS8yMDIzIDExOjQ1CjI3OTUzNTE2LDExLzEvMjAyMyAxMTo1MgoyNzk1NDg1NSwxMS8xLzIwMjMgMTI6MDYKMjc5NTI4MDMsMTEvMS8yMDIzIDExOjQ0CjI3OTUyNzkwLDExLzEvMjAyMyAxMTo0NAoyNzk1NDgxMSwxMS8xLzIwMjMgMTI6MDYK"
    # poisson(base64.b64decode(d).decode())

    app = tornado.web.Application([
        (r"/", MainHandler),
    ])
    app.listen(8888)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
