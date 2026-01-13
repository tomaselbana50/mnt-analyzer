from apscheduler.schedulers.blocking import BlockingScheduler
import high_demand_collector
import discount_analyzer

scheduler = BlockingScheduler()

# تشغيل High Demand كل 6 ساعات
scheduler.add_job(high_demand_collector.run_all_categories, 'interval', hours=6)

# تشغيل Real Discounts كل 6 ساعات
scheduler.add_job(discount_analyzer.run_all_categories, 'interval', hours=6)

scheduler.start()