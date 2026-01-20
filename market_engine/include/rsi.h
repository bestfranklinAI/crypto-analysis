#ifndef RSI_H
#define RSI_H

#include "indicators.h"
#include <deque>

namespace market_engine{
    class RSICalculator: public IndicatorCalculator{
        public:
            explicit RSICalculator(const std::string&symbol, size_t period = 14);

            void add_trade(const Trade& trade) override;
            std::optional<IndicatorResult> get_current() const override;
            void clear() override;

            //RSI specific methods
        void add_price(double price, long long timestamp);
        double get_rsi() const;
        bool is_ready() const;
        bool has_data() const;
        private:
        std:: string symbol_;
            size_t period_;
            std::deque<double> prices_;
            double avg_gain_;
            double avg_loss_;
            bool initialized_;
            long long last_timestamp_;

            void calculate_initial_averages();
            void update_averages(double gain, double loss);


    };
}

#endif