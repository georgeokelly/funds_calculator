from numpy import float32
from fund_nav import *

## Benchmark cases
## case 0:  Every day
## case 1:  Every Mon
## case 2:  Every Tue
## case 3:  Every Wed
## case 4:  Every Thu
## case 5:  Every Fri

def benchmark(df, msg=None):
    latest_nav = np.float32(df.loc[df.index[0]]["NAV"])
    # nav_arr = np.empty(shape=(7, df.index.size), dtype=np.float32)
    nav_types = ["Daily", "Mon", "Tue", "Wed", "Thu", "Fri"]
    nav_dict = dict()
    equity_dict = dict()
    profit_dict = dict()

    ## case 0
    nav_dict[nav_types[0]] = df["NAV"].values.ravel().astype(np.float32)

    ## case 1 - 5
    for weekday in range(1, 6):
        it_nav = df.loc[df["Weekday"] == weekday, ["NAV"]].values.ravel().astype(np.float32)
        nav_dict[nav_types[weekday]] = it_nav

    for it in nav_dict:
        equity_dict[it] = np.sum(1 / nav_dict[it]) * latest_nav

    for it in equity_dict:
        _div = nav_dict[it].shape[0] if nav_dict[it].shape[0] != 0 else 1
        profit = equity_dict[it] / _div
        profit_dict[it] = 0 if np.isnan(profit) else profit

    best_three = sorted(profit_dict.items(), key=lambda x: x[1], reverse=True)[:3]
    # my_logger.info("[{} results] best: {}".format(msg, [it[0] for it in best_three]))
    return best_three


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark for auto-invest")
    parser.add_argument("--fund_code", type=str, default="000051",
                        help="the fund code")
    args = parser.parse_args()
    fund_df = get_fund_nav(args.fund_code, duration=365 * 5)
    my_logger.debug("Fund code: {}, name: {}, size={}\n{}\n...\n{}".format(args.fund_code, get_fund_info(args.fund_code, 2), fund_df.index.size, fund_df.head(5), fund_df.tail(5)))

    ret = list()
    ## Past one month
    duration_choices = [7, 30, 90, 365, 365 * 2, 365 * 3, 365 * 5]
    end_dt = str2date(fund_df["Date"][0])
    for duration in duration_choices:
        start_dt = get_another_day(end_dt, duration)
        ret.append(benchmark(fund_df.loc[fund_df["Date"] >= str(start_dt)], msg="Past {} days".format(duration)))

    my_logger.info("Fund code: {}, name: {}".format(args.fund_code, get_fund_info(args.fund_code, 2)))
    for idx, it_ret in enumerate(ret):
        msg = "[Past {} days]".format(duration_choices[idx]).ljust(18)
        for it in it_ret:
            msg = msg + "{}:".format(it[0]).ljust(7) + "{:.2f}%   ".format(it[1] * 100).rjust(10)
        max_aror = (it_ret[0][1] - 1) / duration_choices[idx] * 360
        msg += "Max AROR: {:.2f}%".format(max_aror * 100)
        my_logger.info(msg)

