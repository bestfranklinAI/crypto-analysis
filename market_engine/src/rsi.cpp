#include "rsi.h"

#include<cmath>
#include <algorithm>


namespace market_engine{

    RSICalculator::RSICalculator(const std::string& symbol, size_t period): 
    symbol_(symbol), 
    period_(period), 
    avg_gain_(0.0), 
    avg_loss_(0.0), 
    initialized_(false), 
    last_timestamp_(0){
        prices_.clear();
    }


    void RSICalculator::add_trade(const Trade& trade){
        add_price(trade.price, trade.timestamp);
    }

    std::optional<IndicatorResult> RSICalculator::get_current() const{
        if (!has_data()){
            return std::nullopt;
        }

        IndicatorResult result;
        result.symbol = symbol_;
        result.vwap = 0.0;
        result.rsi = get_rsi();
        result.timestamp= last_timestamp_;
        result.is_valid = has_data();

        return result;
    }

    void RSICalculator::clear(){
        prices_.clear();
        avg_gain_ = 0.0;
        avg_loss_ = 0.0;
        initialized_ = false;
        last_timestamp_ = 0;
    }

    void RSICalculator::add_price(double price, long long timestamp){
        prices_.push_back(price);
        last_timestamp_ = timestamp;

        //Maintain window size
        if(prices_.size() > period_ + 1){
            prices_.pop_front();
        }

        if(!initialized_ && prices_.size() > period_){
            calculate_initial_averages();
            initialized_ = true;
        }
        else if(initialized_ && prices_.size() > 1){
            double change = prices_.back() - prices_[prices_.size() - 2];
            double gain = std::max(change, 0.0);
            double loss = std::max(-change, 0.0);
            update_averages(gain, loss);
        }
    }

    void RSICalculator::calculate_initial_averages(){
        double total_gain = 0.0;
        double total_loss = 0.0;


        for(size_t i = 1; i < period_; ++i){
            double change = prices_[i] - prices_[i-1];
            if(change > 0){
                total_gain += change;
            } else {
                total_loss += -change;
            }
        }
        avg_gain_ = total_gain / period_;
        avg_loss_ = total_loss / period_;

    }

    void RSICalculator::update_averages(double gain, double loss){
        //Apply wilder's exponential smoothing formula
        avg_gain_ = (avg_gain_ * (period_ - 1) + gain) / period_;
        avg_loss_ = (avg_loss_ * (period_ - 1) + loss) / period_;
    }

    double RSICalculator::get_rsi() const{
        if(!initialized_ || avg_loss_ == 0.0){
            return 50.0;
        }

        double rs = avg_gain_/ avg_loss_;
        return 100.0 - (100.0 / (1.0 +rs));
    }

    bool RSICalculator::is_ready() const{
        return initialized_;
    }

    bool RSICalculator::has_data() const{
        return !prices_.empty();
    }
}