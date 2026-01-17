#ifndef VWAP_H
#define VWAP_H

#include "indicators.h"
#include <deque>


namespace market_engine{

    class VWAPCalculator{
        public:
            explicit VWAPCalculator(size_t window_size = 1000);

            void add_trade(double price, double quantity, long long timestamp);
            double get_vwap() const;
            void clear();
        
        private:
            size_t window_size_;
            std::deque<Trade> trades_;
            double cumulative_pq_;
            double cumulative_q_;

            void update_rolling_window();
    };
}

#endif