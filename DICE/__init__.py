# Load packages
from otree.api import *
import pandas as pd
import numpy as np
import re
import random
from collections import defaultdict
from . import image_utils
import json
from django.core.validators import MinValueValidator, MaxValueValidator

doc = """
Mimic social media feeds with DICE template. 
"""


class C(BaseConstants):
    NAME_IN_URL = 'DICE'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    RULES_TEMPLATE = "DICE/T_Rules.html"
    PRIVACY_TEMPLATE = "DICE/T_Privacy.html"
    TWEET_TEMPLATE = "DICE/T_Tweet.html"
    ATTENTION_TEMPLATE = "DICE/T_Attention_Check.html"
    TOPICS_TEMPLATE = "DICE/T_Trending_Topics.html"
    BANNER_TEMPLATE = "DICE/T_Banner_Ads.html"


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass
# Create variables to capture:


class Player(BasePlayer):
    tweets_json = models.StringField()
    image_options_json = models.StringField()
    prolific_id = models.StringField(default=str(" "))
    first_question = models.StringField(blank=True)
    itemcount_first = models.BooleanField(blank=True, initial=False)
    second_question = models.StringField(blank=True)
    question_order = models.StringField(blank=True)
    logistics_early = models.BooleanField(blank=True, initial=False)
    creates_watermarks_other = models.StringField(blank=True)
    moreposts_image_check_1 = models.StringField(choices=['like', 'neutral', 'dislike'], blank=True)
    moreposts_image_check_2 = models.StringField(choices=['like', 'neutral', 'dislike'], blank=True)
    moreposts_image_check_3 = models.StringField(choices=['like', 'neutral', 'dislike'], blank=True)
    moreposts_image_check_4 = models.StringField(choices=['like', 'neutral', 'dislike'], blank=True)
    moreposts_image_check_5 = models.StringField(choices=['like', 'neutral', 'dislike'], blank=True)

    show_own_claim_real = models.BooleanField()
    show_slider_real = models.BooleanField()
    show_slider_ai = models.BooleanField()
    show_own_claim_ai = models.BooleanField()
    image_feelstrue_followup = models.StringField(blank=True, null=True)
    image_feelsnottrue_followup = models.StringField(blank=True, null=True)
    image_feelsnottrue_answered = models.BooleanField(initial=False)
    image_feelstrue_answered = models.BooleanField(initial=False)

    # ad_condition = models.StringField(doc='indicates the ad condition a player is randomly assigned to') delete?
    # Metadata variables:
    disclaimer = models.StringField(blank=True, null=True)
    screenshot_control = models.StringField()
    screenshot_treatment = models.StringField(blank=True, null=True)
    click_x_real = models.FloatField(blank=True)
    click_x_ai = models.FloatField(blank=True)
    click_y_ai = models.FloatField(blank=True)
    click_y_real = models.FloatField(blank=True)
    assigned_image_id = models.StringField()
    feed_condition_row = models.StringField()
    control_feed_condition_row = models.StringField()
    feed_condition = models.StringField(doc='indicates the feed condition a player is randomly assigned to')
    watermark_condition = models.StringField(doc='indicates the watermark condition a player is randomly assigned to')
    sequence = models.StringField(doc='prints the sequence of tweets based on doc_id')
    # cta = models.BooleanField(doc='indicates whether CTA was clicked or not') # is this the watermark?
    scroll_sequence = models.LongStringField(doc='tracks the sequence of feed items a participant scrolled through.')
    viewport_data = models.LongStringField(doc='tracks the time feed items were visible in a participants viewport.')
    likes_data = models.LongStringField(doc='tracks likes.', blank=True)
    replies_data = models.LongStringField(doc='tracks replies.', blank=True)
    retweets_data = models.LongStringField(doc='tracks retweets.', blank=True)

    touch_capability = models.BooleanField(doc="indicates whether a participant uses a touch device to access survey.",
                                           blank=True)
    device_type = models.StringField(doc="indicates the participant's device type based on screen width.",
                                     blank=True)
    # Consent
    consent = models.StringField(
        choices=[
            ['yes', 'I acknowledge that I have read and consent to the information above.'],
            ['no', 'I do not consent to this study.']
        ],
        label="Consent",
        widget=widgets.RadioSelect
    )
    # Demographics pre-treatment:
    party_id = models.IntegerField(
        label="Generally speaking, do you think of yourself as a Democrat, a Republican, or an Independent?",
        choices=[
            (1, 'Strong Democrat'),
            (2, 'Democrat'),
            (3, 'Lean Democrat'),
            (4, 'Independent'),
            (5, 'Lean Republican'),
            (6, 'Republican'),
            (7, 'Strong Republican')
        ],
        widget=widgets.RadioSelect,
        required=True
    )

    # AI/SMP questions pre-treatment:

    smp_entertaining_pre = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label="I find the content on social media platforms entertaining"
    )

    smp_accuracy_pre = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label='I trust the accuracy of the content on social media platforms'
    )

    smp_enjoyment_pre = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label='I enjoy spending time on social media platforms'
    )

    smp_community_pre = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label='I feel part of a community on social media platforms'
    )

    smp_news_pre = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label='I get my news from social media platforms'
    )
    # How much, if at all, do you trust the information you get from... need to randomize order
    # from pew https://www.pewresearch.org/wp-content/uploads/sites/20/2024/10/SR_24.10.16_media-trust-topline.pdf
    # Assessment of All Images (item count questions):
    accurate_all = models.IntegerField(
        label="How many of the images on the previous social media page do you believe are accurate?",
        choices=list(range(0, 6))
    )
    confidence_accurate = models.IntegerField(
        label="How confident are you in your assessment of accurate images?",
        choices=list(range(0, 101))  # Changed from range(0, 11) to range(0, 101)
    )
    share = models.IntegerField(
        label="How many of the posts on the social media page would you share?",
        choices=list(range(0, 6))
    )
    image_accuracy_ai = models.StringField(blank=True)
    why_click_ai = models.LongStringField(
        label="Why did you click on that spot?",
        blank=False
    )
    why_click_real = models.LongStringField(
        label="Why did you click on that spot?",
        blank=False
    )
    image_claim_ai = models.StringField(blank=True)
    image_claim_true_ai = models.StringField(blank=True)
    image_feelstrue_ai = models.StringField(blank=True)
    image_feelstrue_binary_ai = models.StringField(blank=True)
    image_feelstrue_binary_real = models.StringField(blank=True)
    image_confidence_ai = models.IntegerField(blank=True)
    claim_response_ai = models.LongStringField(blank=True)
    claim_response_real = models.LongStringField(blank=True)
    image_accuracy_real = models.StringField(blank=True)
    image_confidence_real = models.IntegerField(blank=True)
    image_claim_true_real = models.StringField(blank=True)
    image_claim_real = models.StringField(
        blank=True  # claim choices are dynamically added, so don't predefine choices
    )
    image_feelstrue_real = models.StringField(choices=[
            ('Definitely does not feel true', 'Definitely does not feel true'),
            ("Mostly does not feel true", "Mostly does not feel true"),
            ("Not sure", "Not sure"),
            ("Mostly feels true", "Mostly feels true"),
            ("Definitely feels true", "Definitely feels true"),
    ],
        blank=True,
    )

    tweet_data = models.LongStringField()

# AI/SMP Questions Post-Treatment:
    llm_familiarity = models.StringField(
        choices=['Have not heard about them', 'Have heard a little about them but have not tried them out',
                 'Have heard about them and have tried them out',
                 'Use them sometimes in my work or personal life', 'Use them frequently in my work or personal life'],
        label="Before today, how familiar were you with large language models (LLMs), or AI chatbots, like ChatGPT, Gemini, or Claude?",
        widget=widgets.RadioSelect,
        required=None
    )
    use_twitter = models.StringField(
        choices=["Several times a day", "About once a day", "A few days a week", "Every few weeks",
                 "Less often", "Never", "Don't know"],
        label="Twitter/X",
        widget=widgets.RadioSelect
    )

    use_instagram = models.StringField(
        choices=["Several times a day", "About once a day", "A few days a week", "Every few weeks",
                 "Less often", "Never", "Don't know"],
        label="Instagram/Threads",
        widget=widgets.RadioSelect
    )

    use_pinterest = models.StringField(
        choices=["Several times a day", "About once a day", "A few days a week", "Every few weeks",
                 "Less often", "Never", "Don't know"],
        label="Pinterest",
        widget=widgets.RadioSelect
    )

    use_linkedin = models.StringField(
        choices=["Several times a day", "About once a day", "A few days a week", "Every few weeks",
                 "Less often", "Never", "Don't know"],
        label="LinkedIn",
        widget=widgets.RadioSelect
    )

    use_facebook = models.StringField(
        choices=["Several times a day", "About once a day", "A few days a week", "Every few weeks",
                 "Less often", "Never", "Don't know"],
        label="Facebook",
        widget=widgets.RadioSelect
    )

    use_youtube = models.StringField(
        choices=["Several times a day", "About once a day", "A few days a week", "Every few weeks",
                 "Less often", "Never", "Don't know"],
        label="YouTube",
        widget=widgets.RadioSelect
    )

    use_tiktok = models.StringField(
        choices=["Several times a day", "About once a day", "A few days a week", "Every few weeks",
                 "Less often", "Never", "Don't know"],
        label="TikTok",
        widget=widgets.RadioSelect
    )

    use_bluesky = models.StringField(
        choices=["Several times a day", "About once a day", "A few days a week", "Every few weeks",
                 "Less often", "Never", "Don't know"],
        label="Bluesky",
        widget=widgets.RadioSelect
    )

    use_truthsocial = models.StringField(
        choices=["Several times a day", "About once a day", "A few days a week", "Every few weeks",
                 "Less often", "Never", "Don't know"],
        label="Truth Social",
        widget=widgets.RadioSelect
    )

    trust_twitter_posttreatment = models.StringField(
        choices=[
            ['alot', 'A lot'],
            ['some', 'Some'],
            ['not_too_much', 'Not too much'],
            ['not_at_all', 'Not at all'],
            ['no_opinion', 'No opinion']
        ],
        label="Twitter/X",
        widget=widgets.RadioSelect)

    trust_instagram_posttreatment = models.StringField(
        choices=[
            ['alot', 'A lot'],
            ['some', 'Some'],
            ['not_too_much', 'Not too much'],
            ['not_at_all', 'Not at all'],
            ['no_opinion', 'No opinion']
        ],
        label="Instagram/Threads",
        widget=widgets.RadioSelect)
    trust_nationalnews_posttreatment = models.StringField(
        choices=[
            ['alot', 'A lot'],
            ['some', 'Some'],
            ['not_too_much', 'Not too much'],
            ['not_at_all', 'Not at all'],
            ['no_opinion', 'No opinion']
        ],
        label="National news organizations",
        widget=widgets.RadioSelect)
    trust_localnews_posttreatment = models.StringField(
        choices=[
            ['alot', 'A lot'],
            ['some', 'Some'],
            ['not_too_much', 'Not too much'],
            ['not_at_all', 'Not at all'],
            ['no_opinion', 'No opinion']
        ],
        label="Local news organizations",
        widget=widgets.RadioSelect)
    trust_friendsfamily_posttreatment = models.StringField(
        choices=[
            ['alot', 'A lot'],
            ['some', 'Some'],
            ['not_too_much', 'Not too much'],
            ['not_at_all', 'Not at all'],
            ['no_opinion', 'No opinion']
        ],
        label="Friends and family",
        widget=widgets.RadioSelect)
    trust_pinterest_posttreatment = models.StringField(
        choices=[
            ['alot', 'A lot'],
            ['some', 'Some'],
            ['not_too_much', 'Not too much'],
            ['not_at_all', 'Not at all'],
            ['no_opinion', 'No opinion']
        ],
        label="Pinterest",
        widget=widgets.RadioSelect)
    trust_linkedin_posttreatment = models.StringField(
        choices=[
            ['alot', 'A lot'],
            ['some', 'Some'],
            ['not_too_much', 'Not too much'],
            ['not_at_all', 'Not at all'],
            ['no_opinion', 'No opinion']
        ],
        label="LinkedIn",
        widget=widgets.RadioSelect)
    trust_facebook_posttreatment = models.StringField(
        choices=[
            ['alot', 'A lot'],
            ['some', 'Some'],
            ['not_too_much', 'Not too much'],
            ['not_at_all', 'Not at all'],
            ['no_opinion', 'No opinion']
        ],
        label="Facebook",
        widget=widgets.RadioSelect)
    trust_youtube_posttreatment = models.StringField(
        choices=[
            ['alot', 'A lot'],
            ['some', 'Some'],
            ['not_too_much', 'Not too much'],
            ['not_at_all', 'Not at all'],
            ['no_opinion', 'No opinion']
        ],
        label="YouTube",
        widget=widgets.RadioSelect)
    trust_tiktok_posttreatment = models.StringField(
        choices=[
            ['alot', 'A lot'],
            ['some', 'Some'],
            ['not_too_much', 'Not too much'],
            ['not_at_all', 'Not at all'],
            ['no_opinion', 'No opinion']
        ],
        label="TikTok",
        widget=widgets.RadioSelect)
    trust_bluesky_posttreatment = models.StringField(
        choices=[
            ['alot', 'A lot'],
            ['some', 'Some'],
            ['not_too_much', 'Not too much'],
            ['not_at_all', 'Not at all'],
            ['no_opinion', 'No opinion']
        ],
        label="Bluesky",
        widget=widgets.RadioSelect)
    trust_truthsocial_posttreatment = models.StringField(
        choices=[
            ['alot', 'A lot'],
            ['some', 'Some'],
            ['not_too_much', 'Not too much'],
            ['not_at_all', 'Not at all'],
            ['no_opinion', 'No opinion']
        ],
        label="Truth Social",
        widget=widgets.RadioSelect)
    trust_acquaintances_posttreatment = models.StringField(
        choices=[
            ['alot', 'A lot'],
            ['some', 'Some'],
            ['not_too_much', 'Not too much'],
            ['not_at_all', 'Not at all'],
            ['no_opinion', 'No opinion']
        ],
        label="Acquaintances",
        widget=widgets.RadioSelect)

    benefits_ai = models.StringField(
        choices=['Strongly Disagee', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        label='Thinking about society generally, the benefits of artificial intelligence (AI) outweigh the risks',
        widget=widgets.RadioSelect)

    distinguish_ability = models.StringField(
        choices=['Strongly Disagee', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        label='I feel confident in my ability to distinguish real from AI-generated images',
        widget=widgets.RadioSelect)

    smp_entertaining_post = models.StringField(
        choices=['Strongly Disagee', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label="I find the content on social media platforms entertaining"
    )

    smp_accuracy_post = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label='I trust the accuracy of content on social media platforms'
    )

    smp_enjoyment_post = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label='I enjoy spending time on social media platforms'
    )

    smp_community_post = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label='I feel part of a community on social media platforms'
    )

    smp_news_post = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label='I get my news from social media platforms'
    )
    benefits_understanding_watermarks = models.IntegerField(min=1, max=5)

    # Demographics post-treatment:
    age = models.IntegerField(
        choices=list(range(18, 100)),
        label="What is your age?"
    )
    gender = models.StringField(
        label="What is your gender?",
        choices=[
            [1, 'Man'],
            [2, "Woman"],
            [3, "Non-binary / third gender"],
            [4, "Prefer not to say"]
        ]
    )

    state = models.StringField(
        choices=['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
                 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho',
                 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine',
                 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi',
                 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey',
                 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio',
                 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina',
                 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia',
                 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'],
        label="What state do you live in?",
        required=None
    )

    race = models.StringField(
        choices=['White', 'Black or African American', 'Hispanic or Latino/a', 'Asian', 'Other Race or Ethnicity'],
        label="Choose the group listed below that best captures what you consider yourself to be.",
        required=None
    )

    education = models.StringField(
        choices=['Less than high school degree', 'High school graduate (high school diploma or equivalent including GED)',
                 'Some college but no degree', 'Associate degree in college (2-year)', "Bachelor's degree in college (4-year)",
                 "Master's degree", 'Doctoral degree', 'Professional degree (JD, MD)'],
        label="What is the highest level of education that you have completed?",
        required=None
    )
    income = models.StringField(
        choices=['Less than $14,999', '$15,000 to $24,999', '$25,000 to $34,999',
                 '$35,000 to $49,999', '$50,000 to $74,999', '$75,000 to $149,999',
                 '$150,000 to $199,999', '$200,000 or more', 'Prefer not to answer'],
        label="What is your current annual household income before taxes?",
        required=None
    )

    # Logistics Questions:
    all_images = models.IntegerField(
        choices=[(i, str(i)) for i in range(11)],
        widget=widgets.RadioSelect,
        label="How many images did you see on the previous simulated social media page?"
    )
    loading = models.IntegerField(
        label="Did the images load quickly enough for you on the previous social media page?",
        choices=[(1, 'Yes'), (2, 'No')],
        widget=widgets.RadioSelect
    )

    interaction = models.IntegerField(
        choices=[
            (1, 'Yes, I tried and was able to interact.'),
            (2, 'No, I tried but could not interact.'),
            (3, 'I did not try to interact.'),
            (4, "Not sure/Don't remember")
        ],
        widget=widgets.RadioSelect
    )
    study_topic = models.LongStringField(
        label="What do you believe this research study is about? That is, what is the purpose of this study?"
    )
    # political_content = models.IntegerField(
    #     min=0, max=10, label = "In your opinion, how many of the images on the previous social media page contained political content?"
    # )
    political_content = models.IntegerField(
        choices=[(i, str(i)) for i in range(11)],
        widget=widgets.RadioSelect
    )

    watermark_familiarity = models.IntegerField(
        choices=[
            (1, 'Very familiar'),
            (2, 'Somewhat familiar'),
            (3, 'Not familiar at all'),
        ],
        widget=widgets.RadioSelect
    )

    watermark_manipulation_check = models.IntegerField(
        choices=[
            (1, 'Yes'),
            (2, 'No'),
            (3, 'Not sure')
        ],
        widget=widgets.RadioSelect
    )

    watermark_image_check = models.LongStringField(blank=True)

    ethics_influence_political_prefs = models.IntegerField(
        label='Move the slider below to indicate to what extent do you believe the study will influence your political preferences:',
        min=1, max=5
    )

    # Watermark Questions
    clarity_watermarks = models.StringField(choices=['Not at all', 'Slightly', 'Moderately', 'Very', "Extremely"],
                                            label="The watermark/label/information is clear",
                                            widget=widgets.RadioSelect)
    informative_watermarks = models.StringField(choices=['Not at all', 'Slightly', 'Moderately', 'Very', "Extremely"],
                                                label="The watermark/label is informative",
                                                widget=widgets.RadioSelect)
    trustworthy_watermarks = models.StringField(choices=['Not at all', 'Slightly', 'Moderately', 'Very', "Extremely"],
                                                label="The watermark/label is trustworthy",
                                                widget=widgets.RadioSelect)
    biased_watermarks = models.StringField(choices=['Not at all', 'Slightly', 'Moderately', 'Very', "Extremely"],
                                           label="The watermark/label is biased",
                                           widget=widgets.RadioSelect)
    creates_watermarks = models.StringField(blank=True)

    # Debrief
    understand_AI = models.LongStringField()  # or StringField

    consentdebrief = models.StringField(choices=['yes', 'no'])


# FUNCTIONS -----

def creating_session(subsession):
    # Read data and preprocess tweets
    df = read_feed(subsession.session.config['data_path'])
    tweets = preprocessing(df)

    # Convert 'doc_id' to string and strip whitespace once upfront
    df['doc_id'] = df['doc_id'].astype(str).str.strip()

    # Assign random vars and tweets to each player
    for player in subsession.get_players():
        player.participant.vars['itemcount_first'] = random.random() < 0.5

        order = ['AI', 'Real'] if random.random() < 0.5 else ['Real', 'AI']
        player.participant.vars['question_order'] = order
        player.participant.vars['first_question'] = order[0]
        player.participant.vars['second_question'] = order[1]
        player.participant.vars['logistics_early'] = random.random() < 0.1
        player.participant.tweets = tweets  # initial full tweets dataframe

    # Group players by party_id to block treatment assignment
    party_id_groups = defaultdict(list)
    for player in subsession.get_players():
        party_id_groups[player.party_id].append(player)

    # Define treatment types and watermark options
    treatment_types = [
        'Negative Artistic Democrat', 'Negative Artistic Republican',
        'Negative Realistic Democrat', 'Negative Realistic Republican',
        'Positive Artistic Democrat', 'Positive Artistic Republican',
        'Positive Realistic Democrat', 'Positive Realistic Republican'
    ]
    watermark_options = [
        "none", "fb_content_warning", "insta_content_warning",
        "cr_watermark", "cr_watermark_plus_label"
    ]

    # Control categories for control posts sampling
    control_categories = ['sports', 'technology', 'entertainment', 'politics']

    for party_id, players in party_id_groups.items():
        # Use the first player to get the full tweets dataframe for the group
        group_tweets = players[0].participant.tweets

        # Filter treatment and control posts
        treatment_posts = group_tweets[group_tweets['treatment_type'].isin(treatment_types)]
        control_posts = group_tweets[~group_tweets['treatment_type'].isin(treatment_types)]

        if treatment_posts.empty:
            raise ValueError("No treatment posts found for party_id: {}".format(party_id))

        # Shuffle treatment types for this group
        random.shuffle(treatment_types)

        # Create balanced assignment of watermarks for this group
        group_size = len(players)
        watermarks_needed = []
        full_cycles = group_size // len(watermark_options)
        remainder = group_size % len(watermark_options)

        # Add full cycles of all watermark options
        for _ in range(full_cycles):
            watermarks_needed.extend(watermark_options)

        # Add remainder randomly
        if remainder > 0:
            watermarks_needed.extend(random.sample(watermark_options, remainder))

        # Shuffle the final assignment
        random.shuffle(watermarks_needed)

        for i, player in enumerate(players):
            selected_control_posts = []

            # Cycle treatment type for player
            treatment_type = treatment_types[i % len(treatment_types)]

            # Sample one treatment post
            selected_treatment_post = treatment_posts[treatment_posts['treatment_type'] == treatment_type].sample(n=1).copy()

            # Assign treatment post info to player
            assigned_image_id = str(selected_treatment_post['doc_id'].values[0]).strip()
            player.assigned_image_id = assigned_image_id
            # --- Add this block for disclaimer assignment ---
            kamala_ids = {'101', '102', '105', '106', '109', '110', '114'}
            donald_ids = {'103', '104', '107', '108', '111', '112', '113', '115'}
            taylor_trump_id = '116'

            if assigned_image_id in kamala_ids:
                player.disclaimer = "Kamala Harris"
            elif assigned_image_id in donald_ids:
                player.disclaimer = "Donald Trump"
            elif assigned_image_id == taylor_trump_id:
                player.disclaimer = "Taylor Swift and Donald Trump"
            else:
                player.disclaimer = ""

            feed_row = df[df['doc_id'] == assigned_image_id]
            player.feed_condition_row = feed_row.to_json(orient='records') if not feed_row.empty else None

            # Assign watermark from pre-balanced list (blocked by party_id)
            player.watermark_condition = watermarks_needed[i]
            selected_treatment_post['watermark'] = player.watermark_condition

            # Map watermark condition to screenshot column
            watermark_to_column = {
                "none": "screenshot_nowatermark",
                "insta_content_warning": "screenshot_insta",
                "fb_content_warning": "screenshot_fb",
                "cr_watermark": "screenshot_cr",
                "cr_watermark_plus_label": "screenshot_both",
            }
            screenshot_col = watermark_to_column.get(player.watermark_condition)
            if screenshot_col in selected_treatment_post.columns:
                val = selected_treatment_post[screenshot_col].values[0]
                if pd.notna(val):
                    player.screenshot_treatment = val

            # Sample one control post from each control category
            for category in control_categories:
                category_clean = category.strip().lower()
                category_posts = control_posts[control_posts['control'].str.strip().str.lower() == category_clean]

                if not category_posts.empty:
                    selected_post = category_posts.sample(n=1).copy()
                    selected_post['watermark'] = "none"
                    selected_control_posts.append(selected_post.iloc[0])

                    # For politics category, assign extra fields to player
                    if category_clean == 'politics':
                        if 'screenshot_control' in selected_post.columns:
                            player.screenshot_control = selected_post['screenshot_control'].values[0]
                        player.assigned_politics_id = str(selected_post['doc_id'].values[0]).strip()

                        control_feed_row = df[df['doc_id'] == player.assigned_politics_id]
                        if not control_feed_row.empty:
                            player.control_feed_condition_row = control_feed_row.to_json(orient='records')
                        else:
                            print(f"Warning: No control feed row found for doc_id: {player.assigned_politics_id}")
                            player.control_feed_condition_row = None

                        # Debug prints (optional)
                        print(f"Filtering df for doc_id: '{player.assigned_politics_id}'")
                        print(f"Number of matching rows: {len(control_feed_row)}")
                        print(f"Player {player.id_in_group}: politics control doc_id = {player.assigned_politics_id}")
                        print("Politics control feed condition row (JSON):", player.control_feed_condition_row)

            # Combine treatment and control posts into DataFrame
            selected_control_df = pd.DataFrame(selected_control_posts)
            selected_posts_df = pd.concat([selected_treatment_post, selected_control_df], ignore_index=True)

            # ✅ Add this AFTER selected_posts_df is defined
            selected_posts_df['post_type'] = selected_posts_df.apply(
                lambda row: 'treatment' if row['doc_id'] == assigned_image_id else 'control',
                axis=1
            )
            selected_posts_df['treatment_nowatermark'] = selected_posts_df.apply(
                lambda row: row['screenshot_nowatermark'] if row['post_type'] == 'treatment' else None,
                axis=1
            )

            # Shuffle combined posts
            selected_posts_df = selected_posts_df.sample(frac=1).reset_index(drop=True)

            # Assign shuffled posts DataFrame to participant.tweets
            player.participant.tweets = selected_posts_df


# make images (if any) visible
def extract_first_url(text):
    urls = re.findall(r"(?P<url>https?://\S+)", str(text))
    if urls:
        return urls[0]
    return None


# function that reads data
def read_feed(path):
    if re.match(r'^https?://\S+', path):
        if 'github' in path:
            tweets = pd.read_csv(path, sep=';')
        elif 'drive.google.com' in path:
            file_id = path.split('/')[-2]
            download_url = f'https://drive.google.com/uc?id={file_id}'
            tweets = pd.read_csv(download_url, sep=';')
        else:
            raise ValueError("Unrecognized URL format")
    else:
        tweets = pd.read_csv(path)
    return tweets


# some pre-processing
def preprocessing(df):
    # Reformat date if 'datetime' column exists
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
        df['date'] = df['datetime'].dt.strftime('%d %b').str.replace(' ', '. ')
        df['date'] = df['date'].str.replace('^0', '', regex=True)

        # Highlight hashtags: #example
        df['tweet'] = df['tweet'].str.replace(r'\B(\#[a-zA-Z0-9_]+\b)',
                                              r'<span class="text-primary">\g<0></span>', regex=True)

        # Highlight cashtags: $AAPL (NOT $41,493)
        # df['tweet'] = df['tweet'].str.replace(r'\B(\$(?!\d)\w{2,}\b)',
        #                                       r'<span class="text-primary">\g<0></span>', regex=True)

        # Highlight mentions: @someone
        df['tweet'] = df['tweet'].str.replace(r'\B(\@[a-zA-Z0-9_]+\b)',
                                              r'<span class="text-primary">\g<0></span>', regex=True)

        # Highlight links (keep this one last)
        df['tweet'] = df['tweet'].str.replace(
            r'(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])',
            r'<a class="text-primary">\g<0></a>', regex=True)

    # Make numeric information integers and fill NAs with 0
    df['replies'] = df['replies'].fillna(0).astype(int)
    df['retweets'] = df['retweets'].fillna(0).astype(int)
    df['likes'] = df['likes'].fillna(0).astype(int)

    df['media'] = df['media'].apply(extract_first_url)
    df['media'] = df['media'].str.replace("'|,", '', regex=True)
    df['pic_available'] = np.where(df['media'].str.match(pat='http'), True, False)

    # Create a name icon as a profile pic
    df['icon'] = df['username'].str[:2]
    df['icon'] = df['icon'].str.title()

    # Make sure user descriptions do not entail any '' or "" as this complicates visualization
    # Also replace nan with some whitespace
    df['user_description'] = df['user_description'].str.replace("'", '')
    df['user_description'] = df['user_description'].str.replace('"', '')
    df['user_description'] = df['user_description'].fillna(' ')

    # Make number of followers a formatted string
    df['user_followers'] = df['user_followers'].map('{:,.0f}'.format).str.replace(',', '.')

    # Check profile image urls
    df['profile_pic_available'] = True

    # Clean 'treatment_type' column
    df['treatment_type'] = df['treatment_type'].astype(str).str.strip()

    # Optionally fix known typos
    df['treatment_type'] = df['treatment_type'].replace({
        'Negative Artisitic Democrat': 'Negative Artistic Democrat',
        'Positive Artisitic Democrat': 'Positive Artistic Democrat',
        'Negative Artisitic Republican': 'Negative Artistic Republican',
        'Positive Artisitic Republican': 'Positive Artistic Republican'
    })

    return df


# PAGES (ordering, etc.)
class A_Consent(Page):
    form_model = 'player'
    form_fields = ['consent']


class B_SMPsTrust(Page):
    form_model = 'player'
    form_fields = [
        'party_id',
        'use_twitter',
        'use_instagram',
        'use_pinterest',
        'use_linkedin',
        'use_facebook',
        'use_youtube',
        'use_tiktok',
        'use_bluesky',
        'use_truthsocial',
        'smp_entertaining_pre',
        'smp_accuracy_pre',
        'smp_enjoyment_pre',
        'smp_community_pre',
        'smp_news_pre',
    ]

    @staticmethod
    def before_next_page(self, timeout_happened):
        self.prolific_id = self.participant.label


class C_FeedInstructions(Page):
    form_model = 'player'


class C_Feed(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        fields = ['likes_data', 'replies_data', 'touch_capability', 'device_type', 'retweets_data']
        if not player.session.config['topics'] & player.session.config['show_cta']:
            more_fields = ['scroll_sequence', 'viewport_data']   # , 'cta']
        else:
            more_fields = ['scroll_sequence', 'viewport_data']

        return fields + more_fields

    @staticmethod
    def vars_for_template(player: Player):
        # ad = player.ad_condition
        label_available = False
        if player.participant.label is not None:
            label_available = True

        result = dict(
            tweets=player.participant.tweets.to_dict('index'),
            topics=player.session.config['topics'],
            search_term=player.session.config['search_term'],
            label_available=label_available
            # banner_img='img/{}_banner.png'.format(ad),
        )
        return result

    @staticmethod
    def live_method(player, data):
        parts = data.split('=')
        variable_name = parts[0].strip()
        value = eval(parts[1].strip())

        # Use getattr to get the current value of the attribute within the player object
        current_value = getattr(player, variable_name, 0)

        # Perform the addition assignment and update the attribute within the player object
        setattr(player, variable_name, current_value + value)

    @staticmethod
    def before_next_page(player, timeout_happened):
        if hasattr(player.participant, 'tweets'):
            # Save the full feed as JSON
            tweets_json = player.participant.tweets.to_json(orient='records')
            player.tweet_data = tweets_json


class D_ItemCountQuestions_First(Page):
    form_model = 'player'
    form_fields = ['accurate_all', 'confidence_accurate', 'share']

    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('itemcount_first', False)

    @staticmethod
    def before_next_page(self, timeout_happened):
        # Only save if the value actually exists
        if 'itemcount_first' in self.participant.vars:
            self.itemcount_first = self.participant.vars['itemcount_first']


class D_ItemCountQuestions_Last(Page):
    form_model = 'player'
    form_fields = ['accurate_all', 'confidence_accurate', 'share']

    @staticmethod
    def is_displayed(player):
        return not player.participant.vars.get('itemcount_first', False)

    @staticmethod
    def before_next_page(self, timeout_happened):
        # Only save if the value actually exists
        if 'itemcount_first' in self.participant.vars:
            self.itemcount_first = self.participant.vars['itemcount_first']
        for field_name in ['accurate_all', 'confidence_accurate', 'share']:
            new_val = getattr(player, field_name, None)  # CHANGED THIS LINE
            if new_val and not getattr(player, field_name, None):
                setattr(player, field_name, new_val)


class D_DirectQuestions_AI_First(Page):
    form_model = 'player'
    form_fields = [
        'click_x_ai',
        'click_y_ai',
        'image_feelstrue_followup',
        'image_feelsnottrue_followup',
        'image_claim_ai',
        'image_accuracy_ai',
        'image_confidence_ai',
        'claim_response_ai',
        'image_claim_true_ai',
        'image_feelstrue_ai',
        'image_feelstrue_binary_ai',
        'why_click_ai'
    ]

    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('first_question') == 'AI'

    @staticmethod
    def vars_for_template(player):
        row_json_ai = player.control_feed_condition_row
        if not row_json_ai:
            return dict(
                claim_choices_ai=[],
                show_slider_ai=False,
                show_own_claim_ai=False,
                show_feels_true_q=False,
                show_feels_not_true_q=False,
            )

        row_data_ai = json.loads(row_json_ai)[0]
        claims = [row_data_ai[f'Claim {i}'] for i in range(1, 6)
                  if f'Claim {i}' in row_data_ai and pd.notna(row_data_ai[f'Claim {i}'])]

        # Generate random values only if not already set
        if 'show_slider_ai' not in player.participant.vars:
            player.participant.vars['show_slider_ai'] = random.choice([True, False])
        if 'show_own_claim_ai' not in player.participant.vars:
            player.participant.vars['show_own_claim_ai'] = random.choice([True, False])

        # Store in Player for CSV export
        player.show_slider_ai = player.participant.vars['show_slider_ai']
        player.show_own_claim_ai = player.participant.vars['show_own_claim_ai']

        # Use string keys instead of integers
        claim_choices = [(claim, claim) for claim in claims]  # (value, label) both as strings

        return dict(
            claim_choices_ai=claim_choices,
            show_slider_ai=player.show_slider_ai,
            show_own_claim_ai=player.show_own_claim_ai,
        )

    @staticmethod
    def before_next_page(player,
                         timeout_happened):  # FIXED: Changed from (self, timeout_happened) to (player, timeout_happened)
        """Process form data and save participant vars"""

        # Copy first_question and question_order into Player for CSV export
        if 'first_question' in player.participant.vars:
            player.first_question = player.participant.vars['first_question']
        if 'show_slider_ai' in player.participant.vars:
            player.show_slider_ai = player.participant.vars['show_slider_ai']
        if 'show_own_claim_ai' in player.participant.vars:
            player.show_own_claim_ai = player.participant.vars['show_own_claim_ai']
        if 'question_order' in player.participant.vars:
            player.question_order = json.dumps(player.participant.vars['question_order'])

        # Explicitly save follow-up questions (optional, usually automatic)
        player.image_feelstrue_followup = player.image_feelstrue_followup
        player.image_feelsnottrue_followup = player.image_feelsnottrue_followup

        # Process all form fields using existing method
        for field_name in ['why_click_ai', 'image_claim_ai', 'image_claim_true_ai',
                           'image_feelstrue_ai', 'image_feelstrue_binary_ai',
                           'image_confidence_ai', 'claim_response_ai', 'image_accuracy_ai']:
            new_val = player.field_maybe_none(field_name)
            if new_val and not getattr(player, field_name, None):
                setattr(player, field_name, new_val)
                print(f"Saved {field_name}: {new_val}")  # Debug output

        print("=== AI PAGE BEFORE_NEXT_PAGE COMPLETED ===")  # Debug output
class D_DirectQuestions_Real_First(Page):
    form_model = 'player'
    form_fields = [
        # All your existing fields
        'click_x_real',
        'click_y_real',
        'image_feelstrue_followup',
        'image_feelsnottrue_followup',
        'image_claim_real',
        'image_feelstrue_real',
        'image_feelstrue_binary_real',
        'why_click_real',
        # Add the missing fields
        'claim_response_real',
        'image_accuracy_real',
        'image_confidence_real',
        'image_claim_true_real'
    ]

    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('first_question') == 'Real'

    @staticmethod
    def before_next_page(player, timeout_happened):
        # Save values from participant.vars into Player fields for CSV export
        if 'first_question' in player.participant.vars:
            player.first_question = player.participant.vars['first_question']
        if 'show_slider_real' in player.participant.vars:
            player.show_slider_real = player.participant.vars['show_slider_real']
        if 'show_own_claim_real' in player.participant.vars:
            player.show_own_claim_real = player.participant.vars['show_own_claim_real']
        if 'question_order' in player.participant.vars:
            player.question_order = json.dumps(player.participant.vars['question_order'])

        # Debug: Print current field values
        print("=== FIELD VALUES AFTER FORM PROCESSING ===")
        for field_name in ['claim_response_real', 'image_accuracy_real', 'image_confidence_real',
                           'image_claim_true_real']:
            value = getattr(player, field_name, 'NOT SET')
            print(f"{field_name}: {value}")
        print("=== END DEBUG ===")

    @staticmethod
    def vars_for_template(player):
        row_json_real = player.control_feed_condition_row
        if not row_json_real:
            return dict(
                claim_choices_real=[],
                show_slider_real=False,
                show_own_claim_real=False,
                show_feels_true_q=False,
                show_feels_not_true_q=False,
            )

        row_data_real = json.loads(row_json_real)[0]
        claims = [
            row_data_real[f'Claim {i}']
            for i in range(1, 6)
            if f'Claim {i}' in row_data_real and pd.notna(row_data_real[f'Claim {i}'])
        ]

        # Generate random values only if not already set
        if 'show_slider_real' not in player.participant.vars:
            player.participant.vars['show_slider_real'] = random.choice([True, False])
        if 'show_own_claim_real' not in player.participant.vars:
            player.participant.vars['show_own_claim_real'] = random.choice([True, False])

        # Store them in Player immediately for CSV export
        player.show_slider_real = player.participant.vars['show_slider_real']
        player.show_own_claim_real = player.participant.vars['show_own_claim_real']

        return dict(
            claim_choices_real=list(enumerate(claims, start=1)),
            show_slider_real=player.participant.vars['show_slider_real'],
            show_own_claim_real=player.participant.vars['show_own_claim_real'],
        )


class D_DirectQuestions_AI_Second_FeelTrue(Page):
    form_model = 'player'
    form_fields = [
        'click_x_ai', 'click_y_ai', 'image_claim_ai', 'image_feelstrue_followup',
        'image_accuracy_ai', 'image_confidence_ai', 'claim_response_ai',
        'image_claim_true_ai', 'image_feelstrue_binary_ai', 'why_click_ai', 'image_feelstrue_ai'
    ]

    @staticmethod
    def is_displayed(player):
        # Check second_question
        if player.participant.vars.get('second_question') != 'AI':
            print("AI_Second_FeelTrue: skipped because second_question != 'AI'")
            return False

        # Check first_question
        first_q = player.participant.vars.get('first_question')
        if first_q != 'Real':
            print("AI_Second_FeelTrue: skipped because first_question != 'Real'")
            return False

        # Determine if real round = "does not feel true"
        slider_val = getattr(player, 'image_feelstrue_real', None)
        binary_val = getattr(player, 'image_feelstrue_binary_real', None)
        feels_not_true = False

        if slider_val is not None:
            if slider_val in ["Definitely does not feel true", "Mostly does not feel true"]:
                feels_not_true = True
        elif binary_val == 'Does not feel true':
            feels_not_true = True

        if feels_not_true:
            print("Page showing because real round = does not feel true")
            return True
        else:
            print("Page skipped because real round != does not feel true")
            return False

    @staticmethod
    def vars_for_template(player):
        # Load claim data
        row_data = json.loads(player.feed_condition_row)[0]
        claims = [
            row_data[f'Claim {i}'] for i in range(1, 6)
            if f'Claim {i}' in row_data and pd.notna(row_data[f'Claim {i}'])
        ]

        # Generate random values only if not already set
        if 'show_slider_ai' not in player.participant.vars:
            player.participant.vars['show_slider_ai'] = random.choice([True, False])
        if 'show_own_claim_ai' not in player.participant.vars:
            player.participant.vars['show_own_claim_ai'] = random.choice([True, False])

        # Store in Player for CSV export
        player.show_slider_ai = player.participant.vars['show_slider_ai']
        player.show_own_claim_ai = player.participant.vars['show_own_claim_ai']

        return dict(
            claim_choices_ai=list(enumerate(claims, start=1)),
            show_slider_ai=player.show_slider_ai,
            show_own_claim_ai=player.show_own_claim_ai,
        )

    @staticmethod
    def before_next_page(player,
                         timeout_happened):  # FIXED: Changed from (self, timeout_happened) to (player, timeout_happened)
        """Process form data and save participant vars"""

        # Save the follow-up field
        player.image_feelstrue_followup = player.image_feelstrue_followup

        # Process all form fields
        for field_name in ['why_click_ai', 'image_claim_ai', 'image_claim_true_ai',
                           'image_feelstrue_ai', 'image_feelstrue_binary_ai',
                           'image_confidence_ai', 'claim_response_ai', 'image_accuracy_ai']:
            new_val = player.field_maybe_none(field_name)
            if new_val and not getattr(player, field_name, None):
                setattr(player, field_name, new_val)
                print(f"Saved {field_name}: {new_val}")  # Debug output

        print("=== AI_SECOND_FEELTRUE BEFORE_NEXT_PAGE COMPLETED ===")  # Debug output


class D_DirectQuestions_AI_Second_DoesNotFeelTrue(Page):
    form_model = 'player'
    form_fields = [
        'click_x_ai', 'click_y_ai', 'image_claim_ai', 'image_feelsnottrue_followup',
        'why_click_ai', 'image_feelstrue_ai', 'image_feelstrue_binary_ai',
        'image_confidence_ai', 'claim_response_ai',
        # Add missing fields that might be needed
        'image_accuracy_ai', 'image_claim_true_ai'
    ]

    @staticmethod
    def is_displayed(player):
        if player.participant.vars.get('second_question') != 'AI':
            print("AI_Second_DoesNotFeelTrue: skipped because second_question != 'AI'")
            return False

        if player.participant.vars.get('first_question') != 'Real':
            print("AI_Second_DoesNotFeelTrue: skipped because first_question != 'Real'")
            return False

        slider_val = getattr(player, 'image_feelstrue_real', None)
        binary_val = getattr(player, 'image_feelstrue_binary_real', None)

        answered_feels_true = False
        if slider_val is not None:
            if slider_val in ["Definitely feels true", "Mostly feels true", "Not sure"]:
                answered_feels_true = True
        elif binary_val == 'Feels true':
            answered_feels_true = True

        if answered_feels_true:
            print("AI_Second_DoesNotFeelTrue: showing because real round = feels true")
            return True
        else:
            print("AI_Second_DoesNotFeelTrue: skipped because real round != feels true")
            return False

    @staticmethod
    def vars_for_template(player):
        # Load claim data
        row_data = json.loads(player.feed_condition_row)[0]
        claims = [
            row_data[f'Claim {i}'] for i in range(1, 6)
            if f'Claim {i}' in row_data and pd.notna(row_data[f'Claim {i}'])
        ]

        # Generate random values only if not already set
        if 'show_slider_ai' not in player.participant.vars:
            player.participant.vars['show_slider_ai'] = random.choice([True, False])
        if 'show_own_claim_ai' not in player.participant.vars:
            player.participant.vars['show_own_claim_ai'] = random.choice([True, False])

        # Store in Player for CSV export
        player.show_slider_ai = player.participant.vars['show_slider_ai']
        player.show_own_claim_ai = player.participant.vars['show_own_claim_ai']

        return dict(
            claim_choices_ai=list(enumerate(claims, start=1)),
            show_slider_ai=player.show_slider_ai,
            show_own_claim_ai=player.show_own_claim_ai,
        )

    @staticmethod
    def before_next_page(player,
                         timeout_happened):  # FIXED: Changed from (self, timeout_happened) to (player, timeout_happened)
        """Process form data and save participant vars"""

        # Save the follow-up field
        player.image_feelsnottrue_followup = player.image_feelsnottrue_followup

        # Process all form fields
        for field_name in ['why_click_ai', 'image_claim_ai', 'image_claim_true_ai',
                           'image_feelstrue_ai', 'image_feelstrue_binary_ai',
                           'image_confidence_ai', 'claim_response_ai', 'image_accuracy_ai']:
            new_val = player.field_maybe_none(field_name)
            if new_val and not getattr(player, field_name, None):
                setattr(player, field_name, new_val)
                print(f"Saved {field_name}: {new_val}")  # Debug output

        print("=== AI_SECOND_DOESNOTFEELTRUE BEFORE_NEXT_PAGE COMPLETED ===")  # Debug output


class D_DirectQuestions_Real_Second_FeelTrue(Page):
    form_model = 'player'
    form_fields = [
        'click_x_real', 'click_y_real', 'image_feelstrue_followup', 'image_feelsnottrue_followup',
        'image_claim_real', 'image_accuracy_real', 'image_confidence_real',
        'claim_response_real', 'image_claim_true_real',
        'image_feelstrue_real', 'image_feelstrue_binary_real', 'why_click_real'
    ]

    @staticmethod
    def error_message(player, values):
        if values.get('click_x_real') in [None, ''] or values.get('click_y_real') in [None, '']:
            return "Please click on the image to indicate what influenced your decision."

    @staticmethod
    def is_displayed(player):
        if player.participant.vars.get('second_question') != 'Real':
            return False
        if player.participant.vars.get('first_question') != 'AI':
            return False

        # FIXED: Use direct field access
        slider_val = getattr(player, 'image_feelstrue_ai', None)
        binary_val = getattr(player, 'image_feelstrue_binary_ai', None)

        feels_not_true = False

        if slider_val is not None and slider_val != '':
            if slider_val in ["Definitely does not feel true", "Mostly does not feel true"]:
                feels_not_true = True
        elif binary_val == 'Does not feel true':
            feels_not_true = True

        if feels_not_true:
            print("Real_Second_FeelTrue: showing because AI round = does not feel true")
            return True
        else:
            print("Real_Second_FeelTrue: skipped because AI round != does not feel true")
            return False

    @staticmethod
    def vars_for_template(player):
        # Load claim data
        row_data = json.loads(player.control_feed_condition_row)[0]
        claims = [
            row_data[f'Claim {i}'] for i in range(1, 6)
            if f'Claim {i}' in row_data and pd.notna(row_data[f'Claim {i}'])
        ]

        # Generate random values only if not already set
        if 'show_slider_real' not in player.participant.vars:
            player.participant.vars['show_slider_real'] = random.choice([True, False])
        if 'show_own_claim_real' not in player.participant.vars:
            player.participant.vars['show_own_claim_real'] = random.choice([True, False])

        # Store in Player for CSV export
        player.show_slider_real = player.participant.vars['show_slider_real']
        player.show_own_claim_real = player.participant.vars['show_own_claim_real']

        return dict(
            claim_choices_real=list(enumerate(claims, start=1)),
            show_slider_real=player.show_slider_real,
            show_own_claim_real=player.show_own_claim_real,
        )

    @staticmethod
    def before_next_page(player,
                         timeout_happened):  # FIXED: Changed from (self, timeout_happened) to (player, timeout_happened)
        """Process form data and save participant vars"""

        # Save the follow-up field
        player.image_feelstrue_followup = player.image_feelstrue_followup

        # Process all form fields
        for field_name in ['why_click_real', 'image_claim_real', 'image_claim_true_real',
                           'image_feelstrue_real', 'image_feelstrue_binary_real',
                           'image_confidence_real', 'claim_response_real', 'image_accuracy_real']:
            new_val = player.field_maybe_none(field_name)
            if new_val and not getattr(player, field_name, None):
                setattr(player, field_name, new_val)
                print(f"Saved {field_name}: {new_val}")  # Debug output

        print("=== REAL_SECOND_FEELTRUE BEFORE_NEXT_PAGE COMPLETED ===")  # Debug output


class D_DirectQuestions_Real_Second_DoesNotFeelTrue(Page):
    form_model = 'player'
    form_fields = [
        'click_x_real', 'click_y_real', 'image_claim_real', 'image_feelsnottrue_followup',
        'why_click_real', 'image_confidence_real', 'claim_response_real',
        # Add missing fields that are referenced in before_next_page
        'image_claim_true_real', 'image_feelstrue_real', 'image_feelstrue_binary_real', 'image_accuracy_real'
    ]

    @staticmethod
    def is_displayed(player):
        if player.participant.vars.get('second_question') != 'Real':
            print("Real_Second_DoesNotFeelTrue: skipped because second_question != 'Real'")
            return False
        if player.participant.vars.get('first_question') != 'AI':
            print("Real_Second_DoesNotFeelTrue: skipped because first_question != 'AI'")
            return False

        # FIXED: Use direct field access instead of field_maybe_none()
        slider_val = getattr(player, 'image_feelstrue_ai', None)
        binary_val = getattr(player, 'image_feelstrue_binary_ai', None)

        print(f"DEBUG - slider_val: '{slider_val}'")
        print(f"DEBUG - binary_val: '{binary_val}'")

        feels_true = False

        if slider_val is not None and slider_val != '':
            if slider_val in ["Definitely feels true", "Mostly feels true", "Not sure"]:
                feels_true = True
        elif binary_val == 'Feels true':
            feels_true = True

        if feels_true:
            print("Real_Second_DoesNotFeelTrue: showing because AI round = feels true")
            return True
        else:
            print("Real_Second_DoesNotFeelTrue: skipped because AI round != feels true")
            return False
    @staticmethod
    def vars_for_template(player):
        # Load claim data
        row_data = json.loads(player.control_feed_condition_row)[0]
        claims = [
            row_data[f'Claim {i}'] for i in range(1, 6)
            if f'Claim {i}' in row_data and pd.notna(row_data[f'Claim {i}'])
        ]

        # Generate random values only if not already set
        if 'show_slider_real' not in player.participant.vars:
            player.participant.vars['show_slider_real'] = random.choice([True, False])
        if 'show_own_claim_real' not in player.participant.vars:
            player.participant.vars['show_own_claim_real'] = random.choice([True, False])

        # Store in Player for CSV export
        player.show_slider_real = player.participant.vars['show_slider_real']
        player.show_own_claim_real = player.participant.vars['show_own_claim_real']

        return dict(
            claim_choices_real=list(enumerate(claims, start=1)),
            show_slider_real=player.show_slider_real,
            show_own_claim_real=player.show_own_claim_real,
        )

    @staticmethod
    def before_next_page(player,
                         timeout_happened):  # FIXED: Changed from (self, timeout_happened) to (player, timeout_happened)
        """Process form data and save participant vars"""

        # Save the follow-up field
        player.image_feelsnottrue_followup = player.image_feelsnottrue_followup

        # Process all form fields
        for field_name in ['why_click_real', 'image_claim_real', 'image_claim_true_real',
                           'image_feelstrue_real', 'image_feelstrue_binary_real',
                           'image_confidence_real', 'claim_response_real', 'image_accuracy_real']:
            new_val = player.field_maybe_none(field_name)
            if new_val and not getattr(player, field_name, None):
                setattr(player, field_name, new_val)
                print(f"Saved {field_name}: {new_val}")  # Debug output

        print("=== REAL_SECOND_DOESNOTFEELTRUE BEFORE_NEXT_PAGE COMPLETED ===")  # Debug output

class H_Demographics(Page):
    form_model = 'player'
    form_fields = ["age", "gender", "state", "race", "education", "income"]

class F_SMPPostSurvey(Page):
    pass
# def vars_for_template(player: Player):
#     return {
#         'platforms': C.PLATFORMS
#     }

class E_Logistics_Early(Page):
    form_model = "player"
    form_fields = [
        "all_images",
        "loading",
        "interaction",
        "political_content",
        "watermark_familiarity",
        "watermark_manipulation_check",
        "watermark_image_check",
    ]

    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('logistics_early', True)

    @staticmethod
    # In any page that all players see, or in creating_session
    def before_next_page(self, timeout_happened):
        if 'logistics_early' in self.participant.vars:
            self.logistics_early = self.participant.vars['logistics_early']

    @staticmethod
    def vars_for_template(player):
        df = player.participant.tweets  # DataFrame with post data
        # Print all non-empty 'screenshot_control'
        # print("screenshot_control values:")
        # print(df.loc[df['screenshot_control'].notna(), 'screenshot_control'].tolist())
        #
        # # Print all non-empty 'screenshot_nowatermark'
        # print("screenshot_nowatermark values:")
        # print(df.loc[df['screenshot_nowatermark'].notna(), 'screenshot_nowatermark'].tolist())

        # Get all non-null 'screenshot_control' and 'screenshot_nowatermark' values
        options = df['screenshot_control'].dropna().tolist() + df['screenshot_nowatermark'].dropna().tolist()

        # Optional: limit to first 5 if needed
        options = options[:5]

        return dict(image_options=options)


class E_Logistics_After(Page):
    form_model = "player"
    form_fields = [
        "all_images",
        "loading",
        "interaction",
        "political_content",
        "watermark_familiarity",
        "watermark_manipulation_check",
        "watermark_image_check",
    ]
    @staticmethod
    def is_displayed(player):
        return not player.participant.vars.get('logistics_early', False)

    @staticmethod
    def before_next_page(self, timeout_happened):
        if 'logistics_early' in self.participant.vars:
            self.logistics_early = self.participant.vars['logistics_early']
        for field_name in ["all_images", "loading", "interaction", "political_content",
                           "watermark_familiarity", "watermark_manipulation_check", "watermark_image_check"]:
            new_val = self.field_maybe_none(field_name)
            if new_val and not getattr(self, field_name, None):
                setattr(self, field_name, new_val)
    @staticmethod
    def vars_for_template(player):
        df = player.participant.tweets  # DataFrame with post data
        # Print all non-empty 'screenshot_control'
        print("screenshot_control values:")
        print(df.loc[df['screenshot_control'].notna(), 'screenshot_control'].tolist())

        # Print all non-empty 'screenshot_nowatermark'
        print("screenshot_nowatermark values:")
        print(df.loc[df['screenshot_nowatermark'].notna(), 'screenshot_nowatermark'].tolist())
        # Get all non-null 'screenshot_control' and 'screenshot_nowatermark' values
        options = df['screenshot_control'].dropna().tolist() + df['screenshot_nowatermark'].dropna().tolist()

        # Optional: limit to first 5 if needed
        options = options[:5]

        return dict(image_options=options)


class MorePosts(Page):
    form_model = 'player'
    form_fields = ['moreposts_image_check_1',
    'moreposts_image_check_2',
    'moreposts_image_check_3',
                   'moreposts_image_check_4',
                   'moreposts_image_check_5',]

    @staticmethod
    def vars_for_template(player):
        df = player.participant.tweets  # DataFrame with post data
        # Print all non-empty 'screenshot_control'
        print("screenshot_control values:")
        print(df.loc[df['screenshot_control'].notna(), 'screenshot_control'].tolist())

        # Print all non-empty 'screenshot_nowatermark'
        print("screenshot_nowatermark values:")
        print(df.loc[df['screenshot_nowatermark'].notna(), 'screenshot_nowatermark'].tolist())
        # Get all non-null 'screenshot_control' and 'screenshot_nowatermark' values
        options = df['screenshot_control'].dropna().tolist() + df['screenshot_nowatermark'].dropna().tolist()

        # Optional: limit to first 5 if needed
        options = options[:5]

        # When you want to save:
        player.tweets_json = player.participant.tweets.to_json()
        player.image_options_json = json.dumps(options)
        return dict(image_options=options)


class F_Enjoyment(Page):
    pass


class F_Watermarks(Page):
    form_model = "player"
    form_fields = [
        "clarity_watermarks",
        "informative_watermarks",
        "trustworthy_watermarks",
        "biased_watermarks",
        "creates_watermarks",
        "creates_watermarks_other",

    ]

    @staticmethod
    def is_displayed(player):
        return player.watermark_condition != "none"


class G_AISMPQuestions(Page):
    form_model = "player"
    form_fields = ["llm_familiarity", "trust_twitter_posttreatment",
                   "trust_instagram_posttreatment", "trust_nationalnews_posttreatment", "trust_localnews_posttreatment",
                   "trust_friendsfamily_posttreatment", "trust_pinterest_posttreatment", "trust_linkedin_posttreatment",
                   "trust_facebook_posttreatment", "trust_youtube_posttreatment", "trust_tiktok_posttreatment",
                   "trust_bluesky_posttreatment", "trust_truthsocial_posttreatment", "trust_acquaintances_posttreatment",
                   "smp_entertaining_post", "smp_accuracy_post", "smp_enjoyment_post", "smp_community_post",
                   "smp_news_post", "distinguish_ability", "benefits_ai"]


class H_Debrief(Page):
    form_model = "player"
    form_fields = ['understand_AI', 'consentdebrief']

    @staticmethod
    def vars_for_template(player):
        df = player.participant.tweets
        image_list = df['screenshot_nowatermark'].dropna().tolist()
        image = image_list[0] if image_list else None  # get first image or None

        return dict(
            disclaimer=player.disclaimer,
            image_screenshot_nowatermark=image
        )

    @staticmethod
    def _looks_ok(text: str, disclaimer: str) -> bool:
        # Normalize input: replace dashes with spaces, lower case
        text = re.sub(r'[\s-]+', ' ', text, flags=re.I).strip().lower()

        # Normalize disclaimer into options: full, first, last
        disclaimer = disclaimer.strip().lower()
        parts = disclaimer.split()
        first, last = parts[0], parts[-1]
        full = ' '.join(parts)
        name_options = {re.escape(full), re.escape(first), re.escape(last)}

        # Construct the pattern
        pattern = (
            r'^the image (?:of|about) '              # flexible phrasing
            r'(?:' + '|'.join(name_options) + r') '  # name flexibility
            r'is ai(?: |-)?generated\.?$'            # ai-generated or ai generated
        )

        return re.fullmatch(pattern, text, flags=re.I) is not None


class I_PostDebrief(Page):
    form_model = "player"
    form_fields = ['study_topic', 'ethics_influence_political_prefs', 'benefits_understanding_watermarks']


class EndSurvey(Page):
    form_model = 'player'

    @staticmethod
    def js_vars(player):
        return dict(
            completionlink=player.subsession.session.config['completionlink']
        )

    pass


page_sequence = [
    A_Consent,
    B_SMPsTrust,
    C_FeedInstructions,
    C_Feed,
    E_Logistics_Early,
    D_ItemCountQuestions_First,         # shows only if itemcount_first = True
    D_DirectQuestions_Real_First,
    D_DirectQuestions_AI_Second_FeelTrue,
    D_DirectQuestions_AI_Second_DoesNotFeelTrue,
    D_DirectQuestions_AI_First,
    # D_DirectQuestions_Real_Second,
    D_DirectQuestions_Real_Second_DoesNotFeelTrue,
    D_DirectQuestions_Real_Second_FeelTrue,
    D_ItemCountQuestions_Last,          # shows only if itemcount_first = False
    E_Logistics_After,
    MorePosts,
    F_Watermarks,
    G_AISMPQuestions,
    H_Demographics,
    H_Debrief,
    I_PostDebrief,
    EndSurvey,
]


# Captures higher level data about each player
def custom_export(players):
    # header row
    yield ['session', 'participant_code', 'participant_label', 'participant_in_session', 'condition', 'item_sequence',
           'scroll_sequence', 'item_dwell_time', 'likes', 'retweets']
    for p in players:
        participant = p.participant
        session = p.session
        yield [session.code, participant.code, participant.label, p.id_in_group, p.feed_condition, p.sequence,
               p.watermark_condition, p.scroll_sequence, p.viewport_data, p.likes_data, p.replies_data, p.retweets_data]

    # @staticmethod
    # def is_displayed(player):
    #     return len(player.session.config['survey_link']) == 0
    # form_model = 'player'
    #
    # @staticmethod
    # def is_displayed(player):
    #     return len(player.session.config['briefing']) > 0

# class D_Redirect(Page):
#
#     @staticmethod
#     def is_displayed(player):
#         return len(player.session.config['survey_link']) > 0
#
#     @staticmethod
#     def vars_for_template(player: Player):
#         return dict(link=create_redirect(player))
#
#     @staticmethod
#     def js_vars(player):
#         return dict(link=create_redirect(player))
