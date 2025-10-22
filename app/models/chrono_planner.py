from typing import Dict, List, Any, Optional
from datetime import datetime, time, timedelta
import numpy as np
from scipy.optimize import differential_evolution
import logging
from fastapi import HTTPException
from app.core.config import settings
from app.models.schemas import (
    TreatmentSchedule,
    SleepData,
    EnergyReport,
    FastingPlan,
    NutritionRecommendation
)

logger = logging.getLogger(__name__)

class ChronoTherapeuticPlanner:
    """
    Advanced Chrono-Therapeutic Planner with ML optimization,
    caching, and distributed processing capabilities.
    """
    def __init__(self):
        # Initialize components
        self.cache = RedisCache(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT
        )
        self.metrics = MetricsService()
        self.ml_model = MLModel()
        self.preprocessor = DataPreprocessor()
        self.queue = QueueService(
            bootstrap_servers=settings.KAFKA_SERVERS
        )
        
        # Optimization parameters
        self.MIN_FASTING_HOURS = 12
        self.MAX_FASTING_HOURS = 24
        self.PRE_CHEMO_EXTENDED_FAST = 4
        self.OPTIMAL_FEEDING_WINDOW = 8
        
        # Weights for optimization
        self.weights = {
            'treatment_alignment': 0.4,
            'sleep_quality': 0.3,
            'energy_levels': 0.2,
            'ml_prediction': 0.1
        }
        
        # Initialize thread pool
        self.executor = ThreadPoolExecutor(
            max_workers=settings.MAX_WORKERS
        )

    async def generate_fasting_plan(
        self,
        treatment_schedule: TreatmentSchedule,
        sleep_data: SleepData,
        energy_reports: List[EnergyReport]
    ) -> FastingPlan:
        """Generate an optimized fasting schedule"""
        try:
            # Validate inputs
            self._validate_inputs(
                treatment_schedule,
                sleep_data,
                energy_reports
            )
            
            # Calculate optimal fasting windows
            fasting_windows = await self._optimize_fasting_schedule(
                treatment_schedule,
                sleep_data,
                energy_reports
            )
            
            # Generate nutrition recommendations
            nutrition_recs = await self._generate_nutrition_recommendations(
                fasting_windows,
                treatment_schedule
            )
            
            # Create complete fasting plan
            plan = FastingPlan(
                fasting_windows=fasting_windows,
                nutrition_recommendations=nutrition_recs,
                treatment_alignment_score=self._calculate_alignment_score(
                    fasting_windows,
                    treatment_schedule
                ),
                confidence_score=self._calculate_confidence_score(
                    sleep_data,
                    energy_reports
                )
            )
            
            return plan
            
        except Exception as e:
            logger.error(f"Error generating fasting plan: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate fasting plan"
            )

    def _validate_inputs(
        self,
        treatment_schedule: TreatmentSchedule,
        sleep_data: SleepData,
        energy_reports: List[EnergyReport]
    ) -> None:
        """Validate input data"""
        if not treatment_schedule.treatments:
            raise ValueError("Treatment schedule is empty")
            
        if not sleep_data.sleep_records:
            raise ValueError("Sleep data is empty")
            
        if not energy_reports:
            raise ValueError("Energy reports are empty")

    async def _optimize_fasting_schedule(
        self,
        treatment_schedule: TreatmentSchedule,
        sleep_data: SleepData,
        energy_reports: List[EnergyReport]
    ) -> List[Dict[str, Any]]:
        """Optimize fasting schedule using multiple factors"""
        try:
            # Define optimization bounds
            bounds = [(0, 24)]  # Start hour of fasting
            
            # Define objective function
            def objective(x):
                start_hour = x[0]
                score = 0.0
                
                # Treatment alignment score
                score += self.weights['treatment_alignment'] * \
                    self._evaluate_treatment_alignment(
                        start_hour,
                        treatment_schedule
                    )
                
                # Sleep quality alignment
                score += self.weights['sleep_quality'] * \
                    self._evaluate_sleep_alignment(
                        start_hour,
                        sleep_data
                    )
                
                # Energy level alignment
                score += self.weights['energy_levels'] * \
                    self._evaluate_energy_alignment(
                        start_hour,
                        energy_reports
                    )
                
                return -score  # Negative because we want to maximize
            
            # Run optimization
            result = differential_evolution(
                objective,
                bounds,
                maxiter=100,
                popsize=20
            )
            
            optimal_start = result.x[0]
            
            # Generate fasting windows for next 7 days
            windows = []
            current_date = datetime.now()
            
            for i in range(7):
                day = current_date + timedelta(days=i)
                window = self._create_fasting_window(
                    day,
                    optimal_start,
                    treatment_schedule
                )
                windows.append(window)
            
            return windows
            
        except Exception as e:
            logger.error(f"Optimization error: {str(e)}")
            raise

    def _evaluate_treatment_alignment(
        self,
        start_hour: float,
        schedule: TreatmentSchedule
    ) -> float:
        """Evaluate how well fasting aligns with treatment schedule"""
        try:
            alignment_scores = []
            
            for treatment in schedule.treatments:
                # Convert treatment time to hours
                treatment_hour = treatment.time.hour + treatment.time.minute/60
                
                # Calculate hours of fasting before treatment
                fasting_hours = (
                    treatment_hour - start_hour
                ) % 24
                
                # Score based on optimal pre-treatment fasting
                if fasting_hours >= self.MIN_FASTING_HOURS + self.PRE_CHEMO_EXTENDED_FAST:
                    score = 1.0
                else:
                    score = fasting_hours / (
                        self.MIN_FASTING_HOURS + self.PRE_CHEMO_EXTENDED_FAST
                    )
                
                alignment_scores.append(score)
            
            return np.mean(alignment_scores)
            
        except Exception as e:
            logger.error(f"Treatment alignment evaluation error: {str(e)}")
            return 0.0

    def _evaluate_sleep_alignment(
        self,
        start_hour: float,
        sleep_data: SleepData
    ) -> float:
        """Evaluate how well fasting aligns with sleep patterns"""
        try:
            # Get average sleep and wake times
            avg_sleep = self._calculate_average_time(
                sleep_data.sleep_records,
                'sleep_time'
            )
            avg_wake = self._calculate_average_time(
                sleep_data.sleep_records,
                'wake_time'
            )
            
            # Convert to hours
            sleep_hour = avg_sleep.hour + avg_sleep.minute/60
            wake_hour = avg_wake.hour + avg_wake.minute/60
            
            # Calculate optimal fasting start (2 hours before sleep)
            optimal_start = (sleep_hour - 2) % 24
            
            # Calculate deviation from optimal
            deviation = abs(start_hour - optimal_start)
            if deviation > 12:
                deviation = 24 - deviation
            
            # Score based on deviation (0 = worst, 1 = best)
            return 1 - (deviation / 12)
            
        except Exception as e:
            logger.error(f"Sleep alignment evaluation error: {str(e)}")
            return 0.0

    def _evaluate_energy_alignment(
        self,
        start_hour: float,
        energy_reports: List[EnergyReport]
    ) -> float:
        """Evaluate how well fasting aligns with energy patterns"""
        try:
            # Group energy levels by hour
            hourly_energy = {}
            for report in energy_reports:
                hour = report.timestamp.hour
                if hour not in hourly_energy:
                    hourly_energy[hour] = []
                hourly_energy[hour].append(report.energy_level)
            
            # Calculate average energy level for each hour
            avg_energy = {
                h: np.mean(levels) for h, levels in hourly_energy.items()
            }
            
            # Calculate score based on energy levels during feeding window
            feeding_start = (
                start_hour + self.MIN_FASTING_HOURS
            ) % 24
            feeding_hours = range(
                int(feeding_start),
                int(feeding_start + self.OPTIMAL_FEEDING_WINDOW)
            )
            
            # Get average energy during feeding window
            window_energy = []
            for hour in feeding_hours:
                hour = hour % 24
                if hour in avg_energy:
                    window_energy.append(avg_energy[hour])
            
            if not window_energy:
                return 0.0
                
            return np.mean(window_energy) / 10  # Normalize to 0-1
            
        except Exception as e:
            logger.error(f"Energy alignment evaluation error: {str(e)}")
            return 0.0

    def _create_fasting_window(
        self,
        date: datetime,
        start_hour: float,
        schedule: TreatmentSchedule
    ) -> Dict[str, Any]:
        """Create a fasting window for a specific date"""
        try:
            # Check if there's a treatment on this day
            day_treatments = [
                t for t in schedule.treatments
                if t.time.date() == date.date()
            ]
            
            # Adjust fasting duration based on treatments
            base_duration = self.MIN_FASTING_HOURS
            if day_treatments:
                base_duration += self.PRE_CHEMO_EXTENDED_FAST
            
            # Create start and end times
            start_time = time(
                hour=int(start_hour),
                minute=int((start_hour % 1) * 60)
            )
            end_time = time(
                hour=int((start_hour + base_duration) % 24),
                minute=int(((start_hour + base_duration) % 1) * 60)
            )
            
            return {
                'date': date.date(),
                'start_time': start_time,
                'end_time': end_time,
                'duration': base_duration,
                'has_treatment': bool(day_treatments)
            }
            
        except Exception as e:
            logger.error(f"Fasting window creation error: {str(e)}")
            raise

    async def _generate_nutrition_recommendations(
        self,
        fasting_windows: List[Dict[str, Any]],
        schedule: TreatmentSchedule
    ) -> List[NutritionRecommendation]:
        """Generate nutrition recommendations for each fasting window"""
        try:
            recommendations = []
            
            for window in fasting_windows:
                # Basic recommendation
                rec = NutritionRecommendation(
                    date=window['date'],
                    meal_time=window['end_time'],
                    foods=[],
                    nutrients=[],
                    hydration_target=0.0
                )
                
                # Adjust based on treatment
                if window['has_treatment']:
                    rec = await self._adjust_for_treatment(rec)
                
                # Add recommendations for breaking fast
                rec = await self._add_fasting_break_foods(rec)
                
                recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            logger.error(
                f"Nutrition recommendation generation error: {str(e)}"
            )
            raise

    async def _adjust_for_treatment(
        self,
        rec: NutritionRecommendation
    ) -> NutritionRecommendation:
        """Adjust nutrition recommendations for treatment days"""
        try:
            # Add treatment-specific nutrients
            rec.nutrients.extend([
                "Glutamine",
                "Omega-3 fatty acids",
                "Antioxidants"
            ])
            
            # Add treatment-specific foods
            rec.foods.extend([
                "Bone broth",
                "Fermented foods",
                "Leafy greens"
            ])
            
            # Increase hydration target
            rec.hydration_target = 3.0  # liters
            
            return rec
            
        except Exception as e:
            logger.error(f"Treatment adjustment error: {str(e)}")
            raise

    async def _add_fasting_break_foods(
        self,
        rec: NutritionRecommendation
    ) -> NutritionRecommendation:
        """Add recommendations for breaking the fast"""
        try:
            # Add gentle foods for breaking fast
            rec.foods.extend([
                "Vegetable soup",
                "Steamed vegetables",
                "Sprouted grains"
            ])
            
            # Add important nutrients
            rec.nutrients.extend([
                "Electrolytes",
                "B vitamins",
                "Zinc"
            ])
            
            return rec
            
        except Exception as e:
            logger.error(f"Fasting break foods addition error: {str(e)}")
            raise

    def _calculate_average_time(
        self,
        records: List[Dict[str, time]],
        time_key: str
    ) -> time:
        """Calculate average time from a list of time records"""
        try:
            # Convert times to minutes since midnight
            minutes = [
                record[time_key].hour * 60 + record[time_key].minute
                for record in records
            ]
            
            # Calculate average minutes
            avg_minutes = int(np.mean(minutes))
            
            # Convert back to time
            return time(
                hour=avg_minutes // 60,
                minute=avg_minutes % 60
            )
            
        except Exception as e:
            logger.error(f"Average time calculation error: {str(e)}")
            raise

    def _calculate_alignment_score(
        self,
        fasting_windows: List[Dict[str, Any]],
        schedule: TreatmentSchedule
    ) -> float:
        """Calculate how well the plan aligns with treatments"""
        try:
            alignment_scores = []
            
            for window in fasting_windows:
                if window['has_treatment']:
                    # Check if fasting duration is optimal
                    if window['duration'] >= \
                        self.MIN_FASTING_HOURS + self.PRE_CHEMO_EXTENDED_FAST:
                        alignment_scores.append(1.0)
                    else:
                        alignment_scores.append(0.5)
                else:
                    # Check if base fasting duration is met
                    if window['duration'] >= self.MIN_FASTING_HOURS:
                        alignment_scores.append(1.0)
                    else:
                        alignment_scores.append(0.5)
            
            return float(np.mean(alignment_scores))
            
        except Exception as e:
            logger.error(f"Alignment score calculation error: {str(e)}")
            return 0.0

    def _calculate_confidence_score(
        self,
        sleep_data: SleepData,
        energy_reports: List[EnergyReport]
    ) -> float:
        """Calculate confidence score for the plan"""
        try:
            scores = []
            
            # Sleep data quality
            sleep_score = len(sleep_data.sleep_records) / 7  # Normalize to week
            scores.append(min(sleep_score, 1.0))
            
            # Energy reports quality
            energy_score = len(energy_reports) / 14  # Normalize to 2 per day
            scores.append(min(energy_score, 1.0))
            
            # Data recency
            latest_sleep = max(
                r['date'] for r in sleep_data.sleep_records
            )
            latest_energy = max(
                r.timestamp for r in energy_reports
            )
            
            days_since_sleep = (
                datetime.now().date() - latest_sleep
            ).days
            days_since_energy = (
                datetime.now().date() - latest_energy.date()
            ).days
            
            recency_score = 1.0 - (
                (days_since_sleep + days_since_energy) / 28
            )  # 2 weeks threshold
            scores.append(max(recency_score, 0.0))
            
            return float(np.mean(scores))
            
        except Exception as e:
            logger.error(f"Confidence score calculation error: {str(e)}")
            return 0.0