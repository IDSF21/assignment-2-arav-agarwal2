# Goals of the Project
From working on the paper presentations and summaries for 11-631, Data Science Seminar, I was struck with how hard it was to both build and look through the literature graph offered by the Semantic Scholar to find and see the relations between relevant papers. From doing literature surveys before, I know from firsthand experience that there does not seem to be any tools that perform the following functions in total:

1. Allow users to explore the graph of connections between papers, hopping from one paper to another. This allows users to find papers that are directly related to the paper in question, instead of worrying about the relevance of a paper in their collection.
2. Allow users to save their history, recording what papers they go to as papers they might want to read later and allowing them to go back to the last paper they were looking at whenever possible.
3. Allow users to visualize their reading list as a graph of walks from node to node, demonstrating how they came upon the papers in question and not just the order they found them.

Such a tool is important to me, as it would allow me to do tasks like the following:

1. Search the literature around any particular survey paper, and see what are the most and least influential papers they cite. This would help me condense future paper reading efforts, and ensure I do not read too many papers outside of what I find interesting and relevant to my research interests.
2. Search the literature around a hallmark paper, and find papers that use its approach in novel ways. While it is easy to find papers that are cited by current work, it is not easy to do the opposite, and tools that have the opposite information do not make the graphical view of the relations from paper to paper that I am looking at clear. 

To solve this, I proposed and have created the following tool, which does the following:

1. Allows users to search through the space of papers on Semantic Scholar through the Semantic Scholar API, visually helping them perform the Depth-First or Breath-First Search they might want to do to find papers of interest.
2. Allows users to see the citation and year distributions of papers in relation to their paper and of papers on their reading list, which helps them confirm that they have enough papers from specific time-frames for literature reviews, and helps them assess visually a paper's impact, as older papers might have a lot of references from highly cited papers, which could indicate a paper's lasting impact in the literature.
3. Allows users to download the reading list at any point, thus ensuring they can easily transition from using the tool to getting and reading the papers in question.

# Design Decisions

- I chose to view the literature graph as a walk on the total literature graph, namely to make it clearer to the user what papers are on their reading list and how they might have stumbled upon a paper in their survey process.
- Due to how Streamlit's Agraph component works, I have had to make the UI for navigating the graph as a separate dialog, instead of being able to click on the graph to move around on it. This also ensures that the graph does not get too messy during the survey process, as papers with over 1000 references/citations do exist in the dataset, which would be incredibly difficult to work with and visualize.
- I chose to visualize the years and citation counts as histograms, as they tend to be easily understood and easily demonstrate the years/citations of the papers in one's reading list / in the papers that cite / are referred from the currently selected paper. I had thought of doing something else here, such as a stem and leaf plot or some sort of time-line plot, but both of these options would have made it harder to see the frequencies of each year and any gaps in between years, which was the intent. 
- I chose to make the basic information for the paper an expandable dialog, as if I had made the dialog fully expanded all the time, then the navigation would have been difficult to reach. I had considered putting the basic paper information after the navigation information, but that was also annoying, as it prevented me from being able to look at the paper in more depth before looking at the papers around that paper in the citation graph. 

The main way that I personally came to my design was through a lot of trial and error. I had an idea of what information I wanted to display, and how my general navigation should be, but I was unsure exactly how I was going to place it all concisely. I made a few wireframes, and then decided on the format in the submission.

# Process

I spent a total of 18-20 hours on the project:

1. I started off with 2 hours of brainstorming what I was going to do, and figuring out my data source. I ended up with the Semantic Scholar API, which allowed me to look at the literature graph without needing the send the data over to the user, and allowed for the tool to be useful even if I do not update it for a long time. 

2. I then spent 4 hours exploring my data, and seeing how the formatting might affect my analysis. I had to come up with scenarios to handle cases where the Semantic Scholar Paper ID might not be present, and if the title is meaningless, and filter them accordingly. I also better understood the rate limit, and realized I would have to be careful not to query the API too much when I needed more data.

3. I spent 4 more hours constructing the basics of my interface, finding the components I would use to make it ( Streamlit AGraph for the graph interface, e.g.), and seeing what was not intuitive with Streamlit ( like the buttons, as they only refresh the page through a callback )

4. I then spent 8 hours working on the interface, and testing it out to make sure that the functionality existed as intended, and that nothing was out of the ordinary. In this phase, I added features like the back-button and the list of papers to potentially explore, which were the papers that Semantic Scholar listed as "highly influenced" by the main paper. This helped improve the papers I was looking at, and made the interface feel better to look at and use. 

