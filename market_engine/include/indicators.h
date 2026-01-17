#ifndef INDICATORS_H
#define INDICATORS_H

#include <vector>
#include <deque>
#include <string>
#include <ctime>


namespace market_engine{
struct Trade {
    std::string symbol;
    double price;
    double quantity;
    long long timestamp;
    bool is_buyer_market;
};

struct IndicatorResult{
    std::string symbol;
    double vwap;
    double ris;
    long long timestamp;
    bool is_valid;
};

class IndicatorCalculator {
public:
    virtual ~IndicatorCalculator() = default;
    virtual void add_trade(const Trade& trade) = 0;
    virtual std::optional<IndicatorResult> get_current() const = 0;
    virtual void clear() = 0;
};
}

#endif