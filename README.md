# 🏛️ Stortinget Intelligence Dashboard

An advanced analytics platform for exploring voting patterns, party alliances, and political dynamics in the Norwegian Parliament.

#### 1. **Data Presentation**

- **Tabbed Navigation**: Organized content into 5 focused tabs instead of a single scrolling page
- **Interactive Filters**: Multi-select filters for parties and topics in the Rebels section
- **Comparative Visualizations**: Side-by-side charts for better pattern recognition
- **Progressive Disclosure**: Key metrics upfront, details available on-demand

#### 2. **Visualizations**

- **Scatter Plots**: Show vote distribution (For vs Against) with 50/50 reference line
- **Pie Charts**: Visual breakdown of controversial votes and relationship distributions
- **Distribution Histograms**: Show patterns in alliance agreements and controversy scores
- **Network-Style Views**: Party relationships categorized by strength (Allies/Neutral/Adversaries)

#### 3. **Insights & Analytics**

**Tab 1: Alliance Network**

- Symmetric heatmap showing all party pairs
- Strongest and weakest alliance identification
- Distribution of agreement rates across all party pairs
- Visual clustering of political relationships

**Tab 2: Controversy Analysis**

- Interactive slider to control number of displayed votes
- Scatter plot showing all votes on For/Against axes
- Pie chart breakdown of top controversial vote
- Most divisive topic identification
- Score distribution analysis

**Tab 3: The Rebels**

- Party-wise and topic-wise rebel distribution charts
- Top rebel identification (both individual and party)
- Sortable detailed table with all rebel incidents
- Multi-dimensional filtering

**Tab 4: Deep Insights** ⭐ NEW

- Party discipline analysis comparing rebel rates
- Top 10 most independent representatives
- Party relationship network with categorization
- Alliance cluster distribution
- Contextual insights and interpretations

**Tab 5: Topic Explorer** ⭐ NEW

- Topic-specific deep dive
- Controversy distribution per topic
- Party rebel patterns by topic
- Detailed case listings
- Participation metrics

#### 4. **Additional Data Processing**

The enhanced backend processor now tracks:

- **Representative Activity**: Total votes and rebel rate per representative
- **Topic Statistics**: Votes, totals, and average controversy by topic
- **Party Voting Patterns**: For/Against ratios per party
- **Alliance Details**: Total votes and agreements/disagreements

#### 5. **UX Improvements**

- Custom CSS styling for better visual hierarchy
- Insight boxes highlighting key findings
- Metric cards with context
- Loading states and status indicators
- Data freshness timestamps
- Responsive layouts
- Helpful tooltips and explanations

## 📊 Key Features

### Data Insights You Can Explore

1. **Party Alignment Analysis**

   - Which parties vote together most often?
   - Who are the strongest allies and adversaries?
   - How do alliances distribute across the political spectrum?

2. **Controversy Mapping**

   - Which votes had the smallest margins?
   - What topics generate the most division?
   - How do controversial votes distribute across For/Against?

3. **Individual Dissent Tracking**

   - Who votes against their party most frequently?
   - Which parties have the most internal dissent?
   - What topics cause the most rebellion?

4. **Topic Deep Dives**

   - How controversial is each topic on average?
   - Which parties rebel most on specific topics?
   - Vote participation by topic area

5. **Party Discipline Metrics**
   - Rebel count by party (inverse indicator of discipline)
   - Most independent representatives
   - Party relationship categorization

## 🚀 Getting Started

### Prerequisites

```bash
pip install streamlit pandas plotly requests
```

### File Structure

```
project/
├── storting_processor.py  # Backend data processor
├── streamlit_app.py       # Frontend dashboard
└── README.md                        # This file
```

### Running the Dashboard

1. **First Time Setup**

   ```bash
   streamlit run streamlit_app.py
   ```

2. **In the Dashboard**
   - Click "🔄 Refresh Data" in the sidebar
   - Select session (2024-2025 or 2025-2026)
   - Choose number of cases to analyze (10-200)
   - Wait for processing to complete
   - Explore the 5 tabs!

### Data Refresh

- Data is cached for 1 hour to improve performance
- Click refresh to get latest data from Stortinget API
- Last update timestamp shown in sidebar

## 📁 Generated Data Files

The processor creates 6 CSV files:

1. **processed_rebels.csv** - Individual rebel votes
2. **processed_controversy.csv** - Vote controversy scores
3. **processed_alliances.csv** - Party-to-party agreement rates
4. **processed_representative_activity.csv**  Per-representative statistics
5. **processed_topic_stats.csv** Per-topic aggregates
6. **processed_party_patterns.csv** Party voting tendencies

## 🎨 Design Philosophy

This version follows these principles:

1. **Progressive Disclosure**: Show high-level insights first, details on demand
2. **Visual Hierarchy**: Use color, size, and layout to guide attention
3. **Context Over Data**: Every chart includes explanatory insights
4. **Interactive Exploration**: Filters and selections for personalized analysis
5. **Responsive Design**: Works on different screen sizes
6. **Performance**: Caching and efficient data processing

## 🔍 Use Cases

### For Journalists

- Identify unusual voting patterns for stories
- Track representative independence over time
- Find surprising party alignments

### For Political Analysts

- Measure party discipline and cohesion
- Map coalition dynamics
- Identify swing representatives

### For Citizens

- Understand how representatives vote
- See which topics are most divisive
- Track party agreement patterns

### For Researchers

- Export data for further analysis
- Compare sessions over time
- Study voting behavior patterns

## 📈 Future Enhancement Ideas

1. **Time Series Analysis**

   - Track how alliances change throughout session
   - Rebellion trends over time
   - Controversy evolution

2. **Predictive Models**

   - Predict vote outcomes based on party positions
   - Identify potential swing votes
   - Coalition formation patterns

3. **Comparative Analysis**

   - Multi-session comparisons
   - Historical trend analysis
   - Representative career voting patterns

4. **Network Graphs**

   - Interactive party relationship networks
   - Representative similarity clusters
   - Topic-issue mapping

5. **Export & Sharing**
   - PDF report generation
   - Chart export functionality
   - Shareable permalinks to specific views

## 🛠️ Technical Details

### Backend Improvements

- Added tracking for representative activity
- Enhanced topic statistics collection
- Party voting pattern aggregation
- Better error handling and progress reporting

### Frontend Improvements

- Modular tab-based architecture
- Cached data loading with TTL
- Custom CSS for better aesthetics
- Responsive column layouts
- Interactive Plotly charts with hover details

### Performance

- Data caching reduces API calls
- Efficient pandas operations
- Lazy loading of visualizations
- Optimized chart rendering

## 📝 Data Sources

All data comes from the official Stortinget Open Data API:

- **Base URL**: https://data.stortinget.no/eksport
- **Documentation**: https://data.stortinget.no/dokumentasjon-og-hjelp

## 🤝 Contributing

Ideas for improvement:

1. Add time-based filtering
2. Implement representative profiles
3. Add coalition analysis tools
4. Create exportable reports
5. Add comparative session analysis

## ⚖️ License & Usage

This tool is for educational and informational purposes. Data is sourced from public Stortinget APIs.

---

**Built with:** Streamlit, Plotly, Pandas, Python
**Data Source:** Stortinget Open Data API
**Last Updated:** 2026
