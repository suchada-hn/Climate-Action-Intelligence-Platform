"""
Climate Action Intelligence Platform - Main Streamlit Application
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our custom modules
try:
    from backend.rag_system.climate_rag import ClimateRAGSystem
    from backend.data_processors.climate_data_fetcher import ClimateDataFetcher
    from backend.data_processors.impact_tracker import ImpactTracker
    from config import settings
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="ClimateIQ - AI Climate Action Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = "demo_user"
if 'rag_system' not in st.session_state:
    st.session_state.rag_system = None
if 'data_fetcher' not in st.session_state:
    st.session_state.data_fetcher = None
if 'impact_tracker' not in st.session_state:
    st.session_state.impact_tracker = None

@st.cache_resource
def initialize_systems():
    """Initialize the AI systems (cached for performance)"""
    try:
        rag_system = ClimateRAGSystem()
        rag_system.initialize_vectorstore()
        
        data_fetcher = ClimateDataFetcher()
        impact_tracker = ImpactTracker()
        
        return rag_system, data_fetcher, impact_tracker
    except Exception as e:
        logger.error(f"Error initializing systems: {e}")
        return None, None, None

def main():
    """Main application function"""
    
    # Header
    st.title("🌍 ClimateIQ - Your AI Climate Action Partner")
    st.markdown("*Personalized climate solutions powered by IBM watsonx.ai*")
    
    # Initialize systems
    if st.session_state.rag_system is None:
        with st.spinner("Initializing AI systems..."):
            rag_system, data_fetcher, impact_tracker = initialize_systems()
            if rag_system:
                st.session_state.rag_system = rag_system
                st.session_state.data_fetcher = data_fetcher
                st.session_state.impact_tracker = impact_tracker
                st.success("✅ AI systems initialized successfully!")
            else:
                st.error("❌ Failed to initialize AI systems. Some features may not work.")
                return
    
    # Sidebar for user profile
    with st.sidebar:
        st.header("👤 Your Profile")
        
        location = st.text_input("📍 Location", value="New York, NY", help="Enter your city and state/country")
        lifestyle = st.selectbox("🏠 Lifestyle", ["Urban", "Suburban", "Rural"])
        household_size = st.number_input("👥 Household Size", min_value=1, max_value=10, value=2)
        
        st.divider()
        
        # Quick stats
        if st.session_state.impact_tracker:
            try:
                impact_summary = st.session_state.impact_tracker.get_user_impact_summary(st.session_state.user_id, 30)
                if 'total_impact' in impact_summary:
                    st.subheader("📊 Your Impact (30 days)")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("CO2 Saved", f"{impact_summary['total_impact']['co2_saved_kg']:.1f} kg")
                        st.metric("Actions Taken", impact_summary['total_actions'])
                    with col2:
                        st.metric("Energy Saved", f"{impact_summary['total_impact']['energy_saved_kwh']:.1f} kWh")
                        st.metric("Water Saved", f"{impact_summary['total_impact']['water_saved_gallons']:.1f} gal")
            except Exception as e:
                st.error(f"Error loading impact data: {e}")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Action Plan", "📈 Impact Tracker", "💬 AI Assistant", "🌐 Community", "💰 Opportunities"])
    
    with tab1:
        display_action_plan(location, lifestyle, household_size)
    
    with tab2:
        display_impact_tracker()
    
    with tab3:
        display_ai_assistant(location, lifestyle, household_size)
    
    with tab4:
        display_community_platform()
    
    with tab5:
        display_opportunities()

def display_action_plan(location: str, lifestyle: str, household_size: int):
    """Display personalized action plan"""
    st.header("🎯 Your Personalized Climate Action Plan")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🔄 Generate New Action Plan", type="primary"):
            if st.session_state.rag_system:
                with st.spinner("Analyzing your profile and generating recommendations..."):
                    try:
                        user_profile = {
                            'location': location,
                            'lifestyle': lifestyle,
                            'household_size': household_size
                        }
                        
                        # Generate action plan using RAG system
                        response, sources = st.session_state.rag_system.retrieve_and_generate(
                            f"Create a personalized climate action plan for someone living in {location} with {lifestyle} lifestyle and {household_size} people in household",
                            location,
                            user_profile
                        )
                        
                        st.success("✅ Action plan generated!")
                        
                        # Display the plan
                        st.markdown("### 📋 Your Climate Action Plan")
                        st.markdown(response)
                        
                        # Display sources
                        if sources:
                            with st.expander("📚 Supporting Evidence"):
                                for i, source in enumerate(sources[:3]):
                                    st.write(f"**Source {i+1}:** {source.metadata.get('source', 'Climate Data')}")
                                    st.write(source.page_content[:300] + "...")
                                    st.divider()
                        
                    except Exception as e:
                        st.error(f"Error generating action plan: {e}")
            else:
                st.error("AI system not available. Please refresh the page.")
    
    with col2:
        # Quick action buttons
        st.subheader("⚡ Quick Actions")
        
        quick_actions = [
            ("💡 Switch to LED", "led_bulb_replacement"),
            ("🌡️ Adjust Thermostat", "thermostat_adjustment"),
            ("🚲 Bike Instead of Drive", "bike_trip"),
            ("♻️ Recycle Items", "recycling"),
            ("🌱 Plant a Tree", "tree_planted"),
            ("🥗 Eat Plant-Based Meal", "meat_free_meal")
        ]
        
        for action_name, action_type in quick_actions:
            if st.button(action_name, key=f"quick_{action_type}"):
                track_quick_action(action_type, action_name)

def track_quick_action(action_type: str, action_name: str):
    """Track a quick action"""
    if st.session_state.impact_tracker:
        try:
            result = st.session_state.impact_tracker.track_action(
                st.session_state.user_id,
                action_type,
                quantity=1.0,
                description=f"Quick action: {action_name}"
            )
            
            if 'error' not in result:
                st.success(f"✅ {action_name} tracked! {result.get('message', '')}")
                st.balloons()
            else:
                st.error(f"Error tracking action: {result['error']}")
                
        except Exception as e:
            st.error(f"Error tracking action: {e}")

def display_impact_tracker():
    """Display impact tracking dashboard"""
    st.header("📈 Impact Tracker Dashboard")
    
    if not st.session_state.impact_tracker:
        st.error("Impact tracker not available")
        return
    
    # Action logging section
    st.subheader("📝 Log New Action")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        action_type = st.selectbox("Action Type", [
            "led_bulb_replacement",
            "thermostat_adjustment", 
            "car_trip_avoided",
            "bike_trip",
            "public_transport_use",
            "solar_panel_kwh",
            "tree_planted",
            "composting",
            "meat_free_meal",
            "recycling",
            "water_conservation"
        ])
    
    with col2:
        quantity = st.number_input("Quantity", min_value=0.1, value=1.0, step=0.1)
    
    with col3:
        unit = st.text_input("Unit", value="unit")
    
    description = st.text_area("Description (optional)", placeholder="Describe your climate action...")
    
    if st.button("📊 Track Action", type="primary"):
        try:
            result = st.session_state.impact_tracker.track_action(
                st.session_state.user_id,
                action_type,
                quantity,
                unit,
                description=description
            )
            
            if 'error' not in result:
                st.success(f"✅ Action tracked! {result.get('message', '')}")
                
                # Display impact
                impact = result['impact']
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("CO2 Impact", f"{impact['co2_impact']:.2f} kg")
                with col2:
                    st.metric("Energy Impact", f"{impact['energy_impact']:.2f} kWh")
                with col3:
                    st.metric("Water Impact", f"{impact['water_impact']:.2f} gal")
                with col4:
                    st.metric("Waste Impact", f"{impact['waste_impact']:.2f} kg")
            else:
                st.error(f"Error: {result['error']}")
                
        except Exception as e:
            st.error(f"Error tracking action: {e}")
    
    st.divider()
    
    # Impact summary
    try:
        impact_summary = st.session_state.impact_tracker.get_user_impact_summary(st.session_state.user_id, 30)
        
        if 'total_impact' in impact_summary:
            st.subheader("📊 Your 30-Day Impact Summary")
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Actions", impact_summary['total_actions'])
            with col2:
                st.metric("CO2 Saved", f"{impact_summary['total_impact']['co2_saved_kg']:.1f} kg")
            with col3:
                st.metric("Energy Saved", f"{impact_summary['total_impact']['energy_saved_kwh']:.1f} kWh")
            with col4:
                st.metric("Water Saved", f"{impact_summary['total_impact']['water_saved_gallons']:.1f} gal")
            
            # Equivalents
            if 'equivalent_impact' in impact_summary:
                st.subheader("🌟 Impact Equivalents")
                equiv = impact_summary['equivalent_impact']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.info(f"🌳 **{equiv['trees_equivalent']} trees** worth of CO2 absorption")
                with col2:
                    st.info(f"🚗 **{equiv['car_miles_avoided']} miles** of driving avoided")
                with col3:
                    st.info(f"📱 **{equiv['smartphone_charges']}** smartphone charges worth of energy")
            
            # Actions breakdown chart
            if impact_summary['actions_breakdown']:
                st.subheader("📈 Actions Breakdown")
                
                df = pd.DataFrame(impact_summary['actions_breakdown'])
                
                fig = px.bar(
                    df, 
                    x='action_type', 
                    y='co2_impact',
                    title='CO2 Impact by Action Type',
                    labels={'co2_impact': 'CO2 Impact (kg)', 'action_type': 'Action Type'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading impact summary: {e}")

def display_ai_assistant(location: str, lifestyle: str, household_size: int):
    """Display AI chat assistant"""
    st.header("💬 AI Climate Assistant")
    st.markdown("Ask me anything about climate action, sustainability, or environmental impact!")
    
    # Chat interface
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.chat_message("user").write(message['content'])
        else:
            st.chat_message("assistant").write(message['content'])
    
    # Chat input
    if prompt := st.chat_input("Ask about climate action..."):
        # Add user message to history
        st.session_state.chat_history.append({'role': 'user', 'content': prompt})
        st.chat_message("user").write(prompt)
        
        # Generate response
        if st.session_state.rag_system:
            with st.spinner("Thinking..."):
                try:
                    user_profile = {
                        'location': location,
                        'lifestyle': lifestyle,
                        'household_size': household_size
                    }
                    
                    response, sources = st.session_state.rag_system.retrieve_and_generate(
                        prompt, location, user_profile
                    )
                    
                    # Add assistant response to history
                    st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                    st.chat_message("assistant").write(response)
                    
                    # Show sources if available
                    if sources:
                        with st.expander("📚 Sources"):
                            for i, source in enumerate(sources[:2]):
                                st.write(f"**Source {i+1}:** {source.metadata.get('source', 'Climate Data')}")
                                st.write(source.page_content[:200] + "...")
                
                except Exception as e:
                    error_msg = f"I apologize, but I'm experiencing technical difficulties: {e}"
                    st.session_state.chat_history.append({'role': 'assistant', 'content': error_msg})
                    st.chat_message("assistant").write(error_msg)
        else:
            error_msg = "AI assistant is not available. Please refresh the page."
            st.session_state.chat_history.append({'role': 'assistant', 'content': error_msg})
            st.chat_message("assistant").write(error_msg)

def display_community_platform():
    """Display community collaboration features"""
    st.header("🌐 Community Climate Action")
    
    tab1, tab2 = st.tabs(["💡 Share Solution", "🔍 Browse Solutions"])
    
    with tab1:
        st.subheader("💡 Share Your Climate Solution")
        
        solution_title = st.text_input("Solution Title")
        solution_description = st.text_area("Describe your climate solution", height=150)
        solution_category = st.selectbox("Category", [
            "Energy Efficiency",
            "Renewable Energy", 
            "Transportation",
            "Waste Reduction",
            "Water Conservation",
            "Food & Agriculture",
            "Community Engagement"
        ])
        
        if st.button("🚀 Submit Solution"):
            if solution_title and solution_description:
                # Validate solution using AI
                if st.session_state.rag_system:
                    with st.spinner("Validating solution..."):
                        try:
                            validation = st.session_state.rag_system.watsonx_client.validate_climate_solution(
                                f"Title: {solution_title}\nDescription: {solution_description}\nCategory: {solution_category}"
                            )
                            
                            if validation['status'] == 'accepted':
                                st.success("✅ Solution accepted! Thank you for contributing to climate action.")
                                st.balloons()
                            elif validation['status'] == 'needs_review':
                                st.warning("⚠️ Solution needs review. Our team will evaluate it shortly.")
                            else:
                                st.error("❌ Solution needs improvement. Please revise and resubmit.")
                            
                            st.write("**AI Feedback:**")
                            st.write(validation['feedback'])
                            
                        except Exception as e:
                            st.error(f"Error validating solution: {e}")
                else:
                    st.success("✅ Solution submitted! (AI validation not available)")
            else:
                st.error("Please fill in all required fields.")
    
    with tab2:
        st.subheader("🔍 Community Solutions")
        
        # Sample community solutions
        sample_solutions = [
            {
                'title': 'Community Solar Garden',
                'description': 'Organize neighborhood solar panel installation with bulk purchasing discounts.',
                'category': 'Renewable Energy',
                'impact': '40% cost reduction, 60% emissions reduction',
                'votes': 127
            },
            {
                'title': 'Bike Share Program',
                'description': 'Start a community bike sharing program for short trips and commuting.',
                'category': 'Transportation', 
                'impact': '30% reduction in car trips under 3 miles',
                'votes': 89
            },
            {
                'title': 'Food Waste Reduction App',
                'description': 'Mobile app to connect households with excess food to those in need.',
                'category': 'Food & Agriculture',
                'impact': '50% reduction in household food waste',
                'votes': 156
            }
        ]
        
        for solution in sample_solutions:
            with st.expander(f"💡 {solution['title']} ({solution['votes']} votes)"):
                st.write(f"**Category:** {solution['category']}")
                st.write(f"**Description:** {solution['description']}")
                st.write(f"**Expected Impact:** {solution['impact']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.button("👍 Upvote", key=f"upvote_{solution['title']}")
                with col2:
                    st.button("💬 Comment", key=f"comment_{solution['title']}")
                with col3:
                    st.button("🔄 Implement", key=f"implement_{solution['title']}")

def display_opportunities():
    """Display green financing and incentive opportunities"""
    st.header("💰 Green Financing & Opportunities")
    
    tab1, tab2 = st.tabs(["🏛️ Government Incentives", "💳 Green Financing"])
    
    with tab1:
        st.subheader("🏛️ Available Government Incentives")
        
        incentives = [
            {
                'name': 'Federal Solar Tax Credit',
                'description': '30% tax credit for solar panel installation',
                'value': 'Up to $10,000+',
                'deadline': 'December 31, 2032',
                'eligibility': 'Homeowners installing solar panels'
            },
            {
                'name': 'Electric Vehicle Tax Credit',
                'description': 'Federal tax credit for new electric vehicles',
                'value': 'Up to $7,500',
                'deadline': 'Ongoing',
                'eligibility': 'Purchase of qualifying new EVs'
            },
            {
                'name': 'Energy Efficiency Rebates',
                'description': 'Rebates for energy-efficient appliances and upgrades',
                'value': '$500 - $2,000',
                'deadline': 'Varies by program',
                'eligibility': 'Homeowners and renters'
            }
        ]
        
        for incentive in incentives:
            with st.expander(f"💰 {incentive['name']} - {incentive['value']}"):
                st.write(f"**Description:** {incentive['description']}")
                st.write(f"**Value:** {incentive['value']}")
                st.write(f"**Deadline:** {incentive['deadline']}")
                st.write(f"**Eligibility:** {incentive['eligibility']}")
                st.button("📋 Learn More", key=f"incentive_{incentive['name']}")
    
    with tab2:
        st.subheader("💳 Green Financing Options")
        
        financing_options = [
            {
                'name': 'Green Mortgage',
                'description': 'Reduced interest rates for energy-efficient homes',
                'benefit': '0.25-0.5% rate reduction',
                'provider': 'Various lenders'
            },
            {
                'name': 'Solar Loan Program',
                'description': 'Low-interest loans for solar panel installation',
                'benefit': '2-5% APR, $0 down',
                'provider': 'Solar installers & banks'
            },
            {
                'name': 'Energy Efficiency Loan',
                'description': 'Financing for home energy improvements',
                'benefit': 'Up to $50,000, 5-15 year terms',
                'provider': 'Credit unions & banks'
            }
        ]
        
        for option in financing_options:
            with st.expander(f"💳 {option['name']}"):
                st.write(f"**Description:** {option['description']}")
                st.write(f"**Benefit:** {option['benefit']}")
                st.write(f"**Provider:** {option['provider']}")
                st.button("🔗 Apply Now", key=f"financing_{option['name']}")
        
        # ROI Calculator
        st.subheader("📊 ROI Calculator")
        
        col1, col2 = st.columns(2)
        with col1:
            investment_type = st.selectbox("Investment Type", ["Solar Panels", "Heat Pump", "Insulation", "Electric Vehicle"])
            investment_amount = st.number_input("Investment Amount ($)", min_value=1000, value=15000, step=500)
        
        with col2:
            annual_savings = st.number_input("Annual Savings ($)", min_value=100, value=1500, step=100)
            incentive_amount = st.number_input("Incentive Amount ($)", min_value=0, value=4500, step=500)
        
        if st.button("💰 Calculate ROI"):
            net_investment = investment_amount - incentive_amount
            payback_years = net_investment / annual_savings if annual_savings > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Net Investment", f"${net_investment:,.0f}")
            with col2:
                st.metric("Payback Period", f"{payback_years:.1f} years")
            with col3:
                st.metric("20-Year Savings", f"${(annual_savings * 20 - net_investment):,.0f}")

if __name__ == "__main__":
    main()