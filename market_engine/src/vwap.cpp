#include "vwap.h"
#include <algorithm>



namespace market_engine{

    VWAPCalculator::VWAPCalculator(const std::string& symbol, size_t window_size): symbol_(symbol), window_size_(window_size), cumulative_pq_(0.0), cumulative_q_(0.0), last_timestamp_(0){
        trades_.clear();
    }

    void VWAPCalculator::add_trade(const Trade& trade){
        add_trade_direct(trade.price, trade.quantity, trade.timestamp);
    }

    std::optional<IndicatorResult> VWAPCalculator::get_current() const{

        if(!has_data()){
            return std::nullopt;
        }

        IndicatorResult result;
        result.symbol = symbol_;
        result.vwap = get_vwap();
        result.rsi = 0.0;
        result.timestamp = last_timestamp_;
        result.is_valid = has_data();
        return result;
    }

    void VWAPCalculator::clear(){
        trades_.clear();
        cumulative_pq_ = 0.0;
        cumulative_q_ = 0.0;
        last_timestamp_ = 0;
    }


    void VWAPCalculator::add_trade_direct(double price, double quantity, long long timestamp){

        Trade trade;
        trade.symbol = symbol_;
        trade.price = price;
        trade.quantity = quantity;
        trade.timestamp = timestamp;
        trade.is_buyer_maker = false;

        //Add to rolling window
        trades_.push_back(trade);

        //Update running totals
        cumulative_pq_ += price * quantity;
        cumulative_q_ += quantity;
        last_timestamp_ = timestamp;

        //Maintain window size
        update_rolling_window();

    }

    void VWAPCalculator::update_rolling_window(){
        while(trades_.size() > window_size_){
            const Trade& oldest = trades_.front();

            //Subtract oldest trade from trades

            cumulative_pq_ -= oldest.price * oldest.quantity;
            cumulative_q_ -= oldest.quantity;

            //Remove oldest trade from queue
            trades_.pop_front();
        }
    }

    double VWAPCalculator::get_vwap() const{
        if(cumulative_q_ == 0.0){
            return 0.0;
        }
        return cumulative_pq_ / cumulative_q_;
    }

    bool VWAPCalculator::has_data() const{
        return !trades_.empty();
    }

}