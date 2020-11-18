# ColourData.org

## Introduction
A self-calibrating CV testing environment.
This anonymous data collection project is based on the Ishihara colour perception test invented by Shinobu Ishihara, a professor at the University of Tokyo, who first published his tests in 1917.

In the past, Ishihara tests have required and assumed a somewhat "strict" clinical setting for the tests to be administered accurately and the results are only useful for defining people as either colour-deficient or not to a pre-determined threshold. **There's not much information gained.**

What we're trying to do is to better understand where people's colour vision changes and ultimately what impact or purpose it has.

It's "Self Calibrating" because the tests get more difficult over time as more users add data. The colour data and responses are fed into machine learning algorithms which find patterns and adjust the pallets to better test certain ranges of colour based recognition. More information bellow.

## Data Dictionary

####  temps.csv & (temps_multi.csv with multiple locations)
| Field | Description |
| :--- | :--- |
| user | User, registerd in DB as secrets.token_urlsafe(4) |
| correct | Response correct or not (0/1) |
| recorded_result | The response submitted. Used to evaluate 'near miss' responses. |
| mask_image | The image masked within the test plate. |
| cb_type1 | Should be passed by Duranatope type users |
| cb_type2 | Should be passed by Protanope type users |
| ncb | Should be passed by non colour imapred users' |
| datetime | Time for referenceing user or response image |
| pallet_used | The base pallet used before adding random colour |
| pallet_values | the values used including random variation |
| ishihara_list | List of colours used as RGB |
| COLORS_ON | Colours on the mask as RGB |
| COLORS_OFF | Background colours not on the mask as RGB |
| cluster_classification | Classification label from unserpervised learning models. |


## Try it out!
* [Live Version](https://colourdata.org)


## Part 1
Results ("data") is fed into the lake of results and compared to every other set of results we have. From there, we use unsupervised machine learning models to group results and see who else has similar results to the user.

That process usually produces a chart like this one below, where you can clearly see by the lines
that appear where some results show similarities to others.

<img src="/static/user_correlations.png" alt="User responses correlations" width="85%" />

The more red a square is, the more similar that result is to the corresponding user it aligns with.
The bluer a square is, the less it corresponds. This just helps us to make basic groups.

We have a few different machine learning models that we use, some we pre-determine how many groups
we're expecting to appear, and some give us a number of how many groups are automatically found. We
can compare these numbers to see if things appear to be working properly.
</p>
<p>Once we have basic groups, we assign a category label to that group and then we can move on to the
next part of the process.

## Part 2
Part two of the process is to use supervised machine learning models to classify each result in our
data row by row, rather than per user. We use this information to "train" our machine learning
models which make predicting groups more accurate. The result is pretty accurate, around 80% at the
moment, and with the 20% that are not categorized according to what we anticipate, we inspect this
data to see if a new group is emerging. As we collect more data, we expect to see new groups emerge.
There are 8 known types of colour vision impairment, currently, we can identify 3.

<img src="/static/classifications.png" alt="User responses correlations" style="width:95%" />

Each new group identified adds to the overall picture of what human colour vision looks like.

## Part 3
But, it doesn't end there...
We want our test to get better over time, so the third and final part of the process is
self-calibration.


The colours used in the test are actually a little bit different each time from a degree of
randomness used in the image generator. Sometimes the colours are a little more blue, red or green,
some times a bit more vibrant, sometimes a bit flatter. This means that as the results pile in, we
start to see results that are inherently 'vague'.

<img src="/static/bluey1.png" alt="Pallet variation 1" width="30%" /><img src="/static/bluey2.png" alt="Pallet variation 2" width="30%" /><img src="/static/bluey3.png" alt="Pallet variation 3" width="30%" />

It's sometimes a hard idea to grasp, but by being a little bit random, our results can be more
accurate overall. Each person that is doing the test has a slightly different screen, some may be in
a dark room, some may have their screen dimmer than others, so by adding in some randomness, we can
build a deliberately vague model where there are so many tiny variations in our results, we're still
likely to get an accurate pattern overall.

<img src="/static/colours1.png" alt="User responses 3d space 1" width="45%" /><img src="/static/colours2.png" alt="User responses 3d space 2" width="45%" />

We then filter down to the results for particular occurrences, shave off any outliers (again using
machine learning) and pick the most significant responses and use those as the basis for the
fundamental colours the next time around.

What this means is that the test is constantly optimising, pallet by pallet, user by user, response
by response.


## Part 4 (TBC!)
Eventually, we'll keep working on this project so that it can start to display live results and
offer immediate feedback, as well as more variations on responses and colours but for now we're trying to
ensure that the system accurately records and classifies information.

