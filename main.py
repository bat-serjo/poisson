
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
    def get(self):
        print("OOK")
        self.write("OK")
        time.sleep(5)
        self.write("Hello, world")

    @tornado.concurrent.run_on_executor
    def post(self):
        req = tornado.escape.json_decode(self.request.body)
        ret = poisson(base64.b64decode(req['data']).decode())
        self.write(ret)


def poisson(data: str):
    import numpy as np
    import pandas as pd
    import statsmodels.api as sm

    df = pd.read_csv(io.StringIO(data), delimiter=" ")

    x = (df
         .groupby(['eth', 'precinct'])[["stops", "past.arrests"]]
         .sum()
         .reset_index()
         .pipe(pd.get_dummies, columns=['eth', 'precinct'])
         .assign(intercept=1)  # Adds a column called 'intercept' with all values equal to 1.
         .sort_values(by='stops')
         .reset_index(drop=True)
         )

    y = x.pop("stops")

    model_with_ethnicity = sm.GLM(
        y,
        x[['intercept', 'eth_2', 'eth_3']],
        offset=np.log(x["past.arrests"]),
        family=sm.families.Poisson(),
    )
    result_with_ethnicity = model_with_ethnicity.fit()
    return str(result_with_ethnicity.summary())


async def main():
    app = tornado.web.Application([
        (r"/", MainHandler),
    ])
    app.listen(8888)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
