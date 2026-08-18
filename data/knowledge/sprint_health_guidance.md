\# MAQ Sprint Health Guidance



\## Sprint Progress



Sprint progress should compare completed delivery work with the amount of sprint time that has elapsed.



A sprint can appear healthy only when delivery progress is reasonably aligned with elapsed time.



\## Delivery Gap



Delivery Gap is calculated as:



Completion Percentage - Sprint Elapsed Percentage



A negative delivery gap means progress is behind the elapsed sprint timeline.



A positive delivery gap means completion is ahead of elapsed sprint time.



\## MAQ Deterministic Sprint Health Rules



Use the deterministic health status returned by the Azure DevOps tool.



The current development thresholds are:



\- On Track: delivery gap is greater than or equal to -10 percentage points

\- At Risk: delivery gap is between -25 and -10 percentage points

\- Behind: delivery gap is less than -25 percentage points



The language model must not override this deterministic classification.



\## Signals to Review



When sprint health is At Risk or Behind, review:



\- incomplete work items

\- blocked dependencies

\- remaining work

\- current iteration dates

\- delivery gap

\- completion percentage

\- elapsed sprint percentage



\## Management Interpretation



A sprint that is Behind requires attention because progress is materially lower than expected for the time already consumed.



The recommended response should focus on the evidence available from Azure DevOps rather than inventing causes or owners.

