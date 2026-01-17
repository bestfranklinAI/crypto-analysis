#ifndef RSI_H
#define RSI_H

#include <deque>

namespace market_engine{
    class RSICalculator{
        public:
            explicit RSICalculator(size_t period = 14);

            void add_price(double price);
            double get_rsi() const;
            void clear();
            bool is_ready() const;
        
        private:
            size_t period_;
            std::deque<double> prices_;
            double avg_gain_;
            double avg_loss_;
            bool initialized_;

            void calculate_initial_averages();
            void update_averages(double gain, double loss);


    };
}

#endif