#ifndef VWAP_H
#define VWAP_H

#include "indicators.h"
#include <deque>


namespace market_engine{

    class VWAPCalculator: public IndicatorCalculator{
        public:
            explicit VWAPCalculator(const std::string& symbol, size_t window_size = 1000);

            void add_trade(const Trade& trade) override;
            std::optional<IndicatorResult> get_current() const override;
        void clear() override;

        //VWAP specific methods
        double get_vwap() const;
        void add_trade_direct(double price, double quantity, long long timestamp);
        bool has_data() const;
            std:: string symbol_;
            size_t window_size_;
            std::deque<Trade> trades_;
            double cumulative_pq_;
            double cumulative_q_;
            long long last_timestamp_;

            void update_rolling_window();
    };
}

#endif