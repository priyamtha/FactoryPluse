import os
import pandas as pd
import matplotlib.pyplot as plt

def create_sample_dataset():
    """
    Generate synthetic customer signup funnel dataset matching the sequential stages:
    10,000 click signup -> 8,000 enter email -> 6,000 create password -> 5,000 verify email -> 4,000 add payment -> 2,000 make first purchase.
    """
    n = 10000
    
    # Initialize all stages with 0
    data = {
        'user_id': [f"USER_{i:05d}" for i in range(1, n + 1)],
        'signup_completed': [1] * n,  # All 10,000 start by completing signup click
        'email_entered': [0] * n,
        'password_created': [0] * n,
        'email_verified': [0] * n,
        'payment_added': [0] * n,
        'first_purchase': [0] * n
    }
    
    # Progressively set step outputs to 1 for the matching counts:
    # 8,000 enter email
    for i in range(8000):
        data['email_entered'][i] = 1
        
    # 6,000 create password (subset of email entered)
    for i in range(6000):
        data['password_created'][i] = 1
        
    # 5,000 verify email (subset of password created)
    for i in range(5000):
        data['email_verified'][i] = 1
        
    # 4,000 add payment (subset of email verified)
    for i in range(4000):
        data['payment_added'][i] = 1
        
    # 2,000 make first purchase (subset of payment added)
    for i in range(2000):
        data['first_purchase'][i] = 1
        
    return pd.DataFrame(data)


# ---------------------------------------------------------
# TASK 1: Define Funnel Stages and Count Users (1 mark)
# ---------------------------------------------------------
def task_1_funnel_stages(df):
    """
    Count users at each sequential stage.
    Verify that each stage has fewer users than the previous.
    """
    print("=" * 60)
    print("TASK 1: DEFINE FUNNEL STAGES AND COUNT USERS")
    print("=" * 60)
    
    stage1_signup = len(df[df['signup_completed'] == 1])
    stage2_email = len(df[df['email_entered'] == 1])
    stage3_password = len(df[df['password_created'] == 1])
    stage4_verified = len(df[df['email_verified'] == 1])
    stage5_payment = len(df[df['payment_added'] == 1])
    stage6_purchase = len(df[df['first_purchase'] == 1])

    stages = {
        'Sign Up': stage1_signup,
        'Email Entered': stage2_email,
        'Password Created': stage3_password,
        'Email Verified': stage4_verified,
        'Payment Added': stage5_payment,
        'First Purchase': stage6_purchase
    }
    
    print("Funnel stages user counts:")
    for stage, count in stages.items():
        print(f" - {stage}: {count:,} users")
        
    return stages


# ---------------------------------------------------------
# TASK 2: Compute Drop-Off Rate Between Stages (1 mark)
# ---------------------------------------------------------
def task_2_compute_dropoff(stages):
    """
    Compute drop-off as both absolute users lost and drop rate percentage.
    Identify the stage transition with the highest drop-off rate.
    """
    print("\n" + "=" * 60)
    print("TASK 2: COMPUTE DROP-OFF RATE BETWEEN STAGES")
    print("=" * 60)
    
    stage_list = list(stages.values())
    stage_names = list(stages.keys())

    drop_off = []
    for i in range(len(stage_list) - 1):
        users_before = stage_list[i]
        users_after = stage_list[i+1]
        users_lost = users_before - users_after
        drop_pct = (users_lost / users_before) * 100
        
        drop_off.append({
            'from_stage': stage_names[i],
            'to_stage': stage_names[i+1],
            'users_before': users_before,
            'users_after': users_after,
            'users_lost': users_lost,
            'completion_rate_raw': (users_after / users_before),
            'completion_rate': f'{(users_after/users_before)*100:.1f}%',
            'drop_rate_raw': (users_lost / users_before),
            'drop_rate': f'{drop_pct:.1f}%'
        })

    funnel_df = pd.DataFrame(drop_off)
    print("Funnel transitions and drop-off metrics:")
    print(funnel_df[['from_stage', 'to_stage', 'users_lost', 'completion_rate', 'drop_rate']])

    # Find the biggest drop in absolute users
    biggest_drop_idx = funnel_df['users_lost'].idxmax()
    print(f"\nBiggest drop by absolute users lost: {funnel_df.loc[biggest_drop_idx, 'from_stage']} -> {funnel_df.loc[biggest_drop_idx, 'to_stage']} ({funnel_df.loc[biggest_drop_idx, 'users_lost']:,} users)")
    
    # Find the highest drop-off rate by percentage
    highest_pct_idx = funnel_df['drop_rate_raw'].idxmax()
    print(f"Highest drop-off rate by percentage: {funnel_df.loc[highest_pct_idx, 'from_stage']} -> {funnel_df.loc[highest_pct_idx, 'to_stage']} ({funnel_df.loc[highest_pct_idx, 'drop_rate']})")
    
    return funnel_df


# ---------------------------------------------------------
# TASK 3: Visualize Funnel (1 mark)
# ---------------------------------------------------------
def task_3_visualize_funnel(stages, output_path='funnel_chart.png'):
    """
    Create a bar chart showing user count at each stage.
    Annotate each bar with the count.
    Color code to show funnel progression.
    Save the chart with proper labels.
    """
    print("\n" + "=" * 60)
    print("TASK 3: VISUAL COMPARISON (FUNNEL CHART)")
    print("=" * 60)
    
    fig, ax = plt.subplots(figsize=(10, 6))

    # Using a professional gradient representing funnel flow
    colors = ['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#a5f3fc', '#cffafe']
    ax.bar(stages.keys(), stages.values(), color=colors, edgecolor='#e2e8f0', width=0.55)

    ax.set_ylabel('Users', fontsize=12, fontweight='bold')
    ax.set_xlabel('Funnel Stage', fontsize=12, fontweight='bold')
    ax.set_title('Signup Funnel: Volume by Stage', fontsize=14, fontweight='bold', pad=15)
    ax.set_ylim(0, max(stages.values()) * 1.15)
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    # Annotate counts on top of bars
    for stage, count in stages.items():
        ax.text(stage, count + 150, f"{count:,}", ha='center', va='bottom', fontweight='bold', color='#1e293b')

    plt.xticks(rotation=15, ha='right')
    plt.tight_layout()
    
    # Save chart to root and to output directory
    plt.savefig(output_path, dpi=150)
    os.makedirs('output', exist_ok=True)
    plt.savefig(os.path.join('output', output_path), dpi=150)
    plt.close()
    
    print(f"Funnel visualization saved to: '{output_path}' and 'output/{output_path}'")


# ---------------------------------------------------------
# TASK 4: Calculate Business Impact of Each Drop-Off (1 mark)
# ---------------------------------------------------------
def task_4_calculate_impact(funnel_df, revenue_per_customer=100):
    """
    Assign monetary value per customer ($100).
    Calculate revenue impact of each drop-off.
    Rank by business impact (revenue lost descending).
    """
    print("\n" + "=" * 60)
    print("TASK 4: CALCULATE BUSINESS IMPACT OF DROP-OFF")
    print("=" * 60)
    
    impact_analysis = []
    for idx, row in funnel_df.iterrows():
        users_lost = row['users_lost']
        revenue_lost = users_lost * revenue_per_customer
        impact_analysis.append({
            'drop_point': f"{row['from_stage']} -> {row['to_stage']}",
            'users_lost': users_lost,
            'revenue_impact_raw': revenue_lost,
            'revenue_impact': f'${revenue_lost:,.0f}',
            'priority': 'HIGH' if revenue_lost >= 200000 else 'MEDIUM'
        })

    impact_df = pd.DataFrame(impact_analysis)
    
    # Sort by users lost (which aligns directly with revenue lost as LTV is flat)
    ranked_impact = impact_df.sort_values('users_lost', ascending=False)
    print("Drop-off stages ranked by business impact:")
    print(ranked_impact[['drop_point', 'users_lost', 'revenue_impact', 'priority']])
    
    return impact_df


# ---------------------------------------------------------
# TASK 5: Actionable Recommendation (1 mark)
# ---------------------------------------------------------
def task_5_recommendation(funnel_df, revenue_per_customer=100):
    """
    Identify the single highest-priority stage to optimize based on completion drop rates.
    Suggest hypotheses, success criteria, and calculate business recovery value.
    """
    print("\n" + "=" * 60)
    print("TASK 5: ACTIONABLE RECOMMENDATION")
    print("=" * 60)
    
    # The highest percentage drop is Payment Added -> First Purchase (50.0% drop)
    # The highest absolute user drop has a three-way tie at 2,000 users lost:
    # 1. Sign Up -> Email (20% drop)
    # 2. Email -> Password (25% drop)
    # 3. Payment Added -> First Purchase (50% drop)
    # Among these, 'Payment Added' to 'First Purchase' has the largest percentage drop (50.0%), making it the most critical bottleneck.
    highest_pct_idx = funnel_df['drop_rate_raw'].idxmax()
    highest_impact = funnel_df.loc[highest_pct_idx]
    
    recommendation = f"""
FUNNEL OPTIMIZATION PRIORITY:

CRITICAL BOTTLENECK:
Stage: {highest_impact['from_stage']} -> {highest_impact['to_stage']}
Users Lost: {highest_impact['users_lost']:,.0f}
Drop Rate: {highest_impact['drop_rate']}
Revenue Impact: ${highest_impact['users_lost'] * revenue_per_customer:,.0f}

ROOT CAUSE INVESTIGATION NEEDED:
- Is step unclear? (Poor UX: User payment goes through but checkout button/action is not obvious)
- Is step too complex? (System/session timeouts, excessive verification checks post-payment)
- Is step optional? (Should checkout purchase flow be triggered automatically after adding payment?)
- Is step timing wrong? (Too early/late: Maybe payment details should be requested during checkout, rather than before)

RECOMMENDED ACTION:
1. A/B test simplified version of step (e.g., combine payment details entry with the checkout summary screen)
2. Monitor drop rate before/after implementation
3. Estimate revenue recovery on test segments
4. Roll out to 100% of traffic if conversion improvement > 5%

EXPECTED IMPACT:
If we improve {highest_impact['from_stage']} -> {highest_impact['to_stage']} completion by 10% (reducing drop rate from 50% to 45%):
Additional conversions: {int(highest_impact['users_lost'] * 0.1):,.0f} users
Additional revenue: ${int(highest_impact['users_lost'] * 0.1 * revenue_per_customer):,.0f}
"""
    print(recommendation)
    return recommendation


def run_pipeline():
    """Execute complete Signup Funnel Analysis Pipeline."""
    print("Generating synthetic signup funnel dataset...")
    df = create_sample_dataset()
    
    # Calculate and print baseline conversion rate
    signup_users = len(df[df['signup_completed'] == 1])
    purchase_users = len(df[df['first_purchase'] == 1])
    print(f"Baseline funnel conversion rate: {(purchase_users/signup_users)*100:.1f}%\n")
    
    # Execute tasks
    stages = task_1_funnel_stages(df)
    funnel_df = task_2_compute_dropoff(stages)
    task_3_visualize_funnel(stages, output_path='funnel_chart.png')
    task_4_calculate_impact(funnel_df, revenue_per_customer=100)
    task_5_recommendation(funnel_df, revenue_per_customer=100)
    
    print("=" * 60)
    print("FUNNEL ANALYSIS PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == '__main__':
    run_pipeline()
