"""
Chart Generation for PDF Reports
Helper functions to create data visualizations
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import tempfile
import os
from collections import Counter
from datetime import datetime, timedelta

def create_user_growth_chart(users, conversations):
    """Create user growth trend chart"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    chart_path = temp_file.name
    temp_file.close()

    try:
        fig, ax = plt.subplots(figsize=(7, 4))

        # Get last 7 days of data
        dates = []
        user_counts = []
        conv_counts = []

        for i in range(6, -1, -1):
            date = datetime.now() - timedelta(days=i)
            dates.append(date.strftime('%m/%d'))

            # Count users created on this day
            day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            user_count = sum(1 for u in users if u.created_at and day_start <= u.created_at < day_end)
            conv_count = sum(1 for c in conversations if c.start_time and day_start <= c.start_time < day_end)

            user_counts.append(user_count)
            conv_counts.append(conv_count)

        # Plot
        x = range(len(dates))
        ax.plot(x, user_counts, marker='o', linewidth=2, color='#3498db', label='New Users')
        ax.plot(x, conv_counts, marker='s', linewidth=2, color='#27ae60', label='Conversations')

        ax.set_xlabel('Date', fontsize=10, fontweight='bold')
        ax.set_ylabel('Count', fontsize=10, fontweight='bold')
        ax.set_title('7-Day User Activity Trend', fontsize=12, fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(dates, rotation=45)
        ax.legend(loc='upper left', frameon=True, shadow=True)
        ax.grid(True, alpha=0.3, linestyle='--')

        plt.tight_layout()
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()

        return chart_path
    except Exception as e:
        print(f"Error creating user growth chart: {e}")
        if os.path.exists(chart_path):
            os.unlink(chart_path)
        return None


def create_crop_distribution_chart(conversations):
    """Create crop mentions pie chart"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    chart_path = temp_file.name
    temp_file.close()

    try:
        # Count crop mentions
        crop_counts = Counter()
        for conv in conversations:
            if hasattr(conv, 'get_mentioned_crops'):
                for crop in conv.get_mentioned_crops():
                    crop_counts[crop.lower().capitalize()] += 1

        if not crop_counts:
            # Create "No data" chart
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.text(0.5, 0.5, 'No crop data available yet',
                   ha='center', va='center', fontsize=14, color='gray')
            ax.axis('off')
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            return chart_path

        # Get top 8 crops
        top_crops = dict(crop_counts.most_common(8))

        # Create pie chart
        fig, ax = plt.subplots(figsize=(7, 5))

        colors_palette = ['#3498db', '#27ae60', '#f39c12', '#e74c3c',
                         '#9b59b6', '#1abc9c', '#34495e', '#16a085']

        wedges, texts, autotexts = ax.pie(
            top_crops.values(),
            labels=top_crops.keys(),
            autopct='%1.1f%%',
            startangle=90,
            colors=colors_palette,
            explode=[0.05 if i == 0 else 0 for i in range(len(top_crops))]
        )

        # Enhance text
        for text in texts:
            text.set_fontsize(10)
            text.set_fontweight('bold')

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')

        ax.set_title('Top Discussed Crops Distribution', fontsize=13, fontweight='bold', pad=20)

        plt.tight_layout()
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()

        return chart_path
    except Exception as e:
        print(f"Error creating crop chart: {e}")
        if os.path.exists(chart_path):
            os.unlink(chart_path)
        return None


def create_feedback_rating_chart(feedbacks):
    """Create feedback satisfaction bar chart"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    chart_path = temp_file.name
    temp_file.close()

    try:
        if not feedbacks:
            # Create "No data" chart
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.text(0.5, 0.5, 'No feedback data available yet',
                   ha='center', va='center', fontsize=14, color='gray')
            ax.axis('off')
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            return chart_path

        # Count ratings
        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for fb in feedbacks:
            if fb.overall_rating:
                rating_counts[fb.overall_rating] = rating_counts.get(fb.overall_rating, 0) + 1

        # Create bar chart
        fig, ax = plt.subplots(figsize=(7, 4))

        ratings = list(rating_counts.keys())
        counts = list(rating_counts.values())

        colors = ['#e74c3c', '#f39c12', '#f1c40f', '#27ae60', '#2ecc71']
        bars = ax.bar(ratings, counts, color=colors, edgecolor='black', linewidth=1.5)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontweight='bold', fontsize=10)

        ax.set_xlabel('Rating (Stars)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Number of Responses', fontsize=11, fontweight='bold')
        ax.set_title('User Satisfaction Ratings', fontsize=13, fontweight='bold', pad=15)
        ax.set_xticks(ratings)
        ax.set_xticklabels([f'{r}★' for r in ratings])
        ax.grid(True, axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)

        plt.tight_layout()
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()

        return chart_path
    except Exception as e:
        print(f"Error creating feedback chart: {e}")
        if os.path.exists(chart_path):
            os.unlink(chart_path)
        return None


def create_regional_distribution_chart(users):
    """Create regional user distribution horizontal bar chart"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    chart_path = temp_file.name
    temp_file.close()

    try:
        # Count users by region
        region_counts = Counter()
        for user in users:
            if user.region:
                region_name = user.region.value if hasattr(user.region, 'value') else user.region
                region_counts[region_name] += 1

        if not region_counts:
            # Create "No data" chart
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.text(0.5, 0.5, 'No regional data available yet',
                   ha='center', va='center', fontsize=14, color='gray')
            ax.axis('off')
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            return chart_path

        # Sort by count
        sorted_regions = sorted(region_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        regions = [r[0] for r in sorted_regions]
        counts = [r[1] for r in sorted_regions]

        # Create horizontal bar chart
        fig, ax = plt.subplots(figsize=(7, 5))

        colors_gradient = plt.cm.viridis(range(len(regions)))
        bars = ax.barh(regions, counts, color=colors_gradient, edgecolor='black', linewidth=1)

        # Add value labels
        for i, (bar, count) in enumerate(zip(bars, counts)):
            ax.text(count + max(counts)*0.02, i, str(count),
                   va='center', fontweight='bold', fontsize=9)

        ax.set_xlabel('Number of Users', fontsize=11, fontweight='bold')
        ax.set_title('User Distribution by Region', fontsize=13, fontweight='bold', pad=15)
        ax.grid(True, axis='x', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)

        plt.tight_layout()
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()

        return chart_path
    except Exception as e:
        print(f"Error creating regional chart: {e}")
        if os.path.exists(chart_path):
            os.unlink(chart_path)
        return None
