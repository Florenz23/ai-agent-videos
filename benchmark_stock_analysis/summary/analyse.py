import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Read the CSV data
df = pd.read_csv('framework_comparison.csv')

# Set the style for the plots
plt.style.use('seaborn')

# Create a figure with subplots
fig, axs = plt.subplots(2, 2, figsize=(20, 20))
fig.suptitle('AI Framework Comparison', fontsize=16)

# 1. Cost and Total Tokens
ax1 = axs[0, 0]
ax1.bar(df['Framework'], df['Cost'])
ax1.set_title('Cost per Run')
ax1.set_ylabel('Cost ($)')
ax1.tick_params(axis='x', rotation=45)

ax1_twin = ax1.twinx()
ax1_twin.plot(df['Framework'], df['Total Tokens'], 'r-o')
ax1_twin.set_ylabel('Total Tokens', color='r')
ax1_twin.tick_params(axis='y', labelcolor='r')

# 2. Lines of Code Comparison
ax2 = axs[0, 1]
ax2.bar(df['Framework'], df['Lines of Code (Excluding Tool)'], label='Excluding Tool')
ax2.bar(df['Framework'], df['Lines of Code (Tool Usage)'], bottom=df['Lines of Code (Excluding Tool)'], label='Tool Usage')
ax2.set_title('Lines of Code Comparison')
ax2.set_ylabel('Number of Lines')
ax2.legend()
ax2.tick_params(axis='x', rotation=45)

# 3. Execution Time
ax3 = axs[1, 0]
ax3.bar(df['Framework'], df['Execution Time (s)'])
ax3.set_title('Execution Time')
ax3.set_ylabel('Time (seconds)')
ax3.tick_params(axis='x', rotation=45)

# 4. Ease of Use and Installation Complexity
ax4 = axs[1, 1]
ease_of_use_map = {'Easy': 1, 'Medium': 2, 'Hard': 3}
installation_complexity_map = {'Low': 1, 'Medium': 2, 'High': 3}

df['Ease of Use Numeric'] = df['Ease of Use'].map(ease_of_use_map)
df['Installation Complexity Numeric'] = df['Installation Complexity'].map(installation_complexity_map)

ax4.scatter(df['Ease of Use Numeric'], df['Installation Complexity Numeric'], s=100)
for i, txt in enumerate(df['Framework']):
    ax4.annotate(txt, (df['Ease of Use Numeric'][i], df['Installation Complexity Numeric'][i]), xytext=(5,5), textcoords='offset points')

ax4.set_xticks([1, 2, 3])
ax4.set_yticks([1, 2, 3])
ax4.set_xticklabels(['Easy', 'Medium', 'Hard'])
ax4.set_yticklabels(['Low', 'Medium', 'High'])
ax4.set_xlabel('Ease of Use')
ax4.set_ylabel('Installation Complexity')
ax4.set_title('Ease of Use vs Installation Complexity')

plt.tight_layout()
plt.savefig('framework_comparison.png')
plt.show()