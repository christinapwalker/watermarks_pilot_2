# Load packages
from otree.api import *
import pandas as pd
import numpy as np
import re
import random
from collections import defaultdict
from . import image_utils
import json
from django.utils.safestring import mark_safe
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

# Variables to capture:
class Player(BasePlayer):
    tweets_json = models.StringField()
    assigned_politics_id = models.StringField(blank=True)
    claim_real = models.StringField()
    claim_ai = models.StringField(blank=True)
    shown_info_treatment = models.BooleanField(
        doc="Indicates whether the player was shown the info treatment page"
    )
    watermark_statements_order = models.StringField(blank=True)
    creates_watermarks_order = models.StringField(blank=True)
    social_media_order = models.StringField(blank=True)
    image_options_json = models.StringField()
    prolific_id = models.StringField(default=str(" "))
    first_question = models.StringField(blank=True)
    second_question = models.StringField(blank=True)
    question_order = models.StringField(blank=True)
    creates_watermarks_other = models.StringField(blank=True)
    moreposts_image_check_1 = models.StringField(choices=['like', 'neutral', 'dislike'], blank=True)
    moreposts_image_check_2 = models.StringField(choices=['like', 'neutral', 'dislike'], blank=True)
    moreposts_image_check_3 = models.StringField(choices=['like', 'neutral', 'dislike'], blank=True)
    moreposts_image_check_4 = models.StringField(choices=['like', 'neutral', 'dislike'], blank=True)
    moreposts_image_check_5 = models.StringField(choices=['like', 'neutral', 'dislike'], blank=True)
    familiarity_real = models.StringField(blank=True)
    familiarity_ai = models.StringField(blank=True)
    attention_check = models.LongStringField(
        blank=True,
        label="Please check all words that describe how you are currently feeling."
    )

    color_check = models.LongStringField(
        blank=True,
        label="What is your favorite color?"
    )

    insta_uncover_clicks = models.LongStringField(
        doc='Tracks clicks on Instagram "uncover photo" button with timestamps',
        blank=True
    )
    smp_post_order = models.StringField(blank=True)

    watermark_hover_events = models.LongStringField(
        doc='Tracks hover events on CR watermark with timestamps',
        blank=True
    )
    smp_order = models.StringField(blank=True)

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
    watermark_condition = models.StringField(doc='indicates the watermark condition a player is randomly assigned to')
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


    watermark_familiarity = models.StringField(
        choices=[
            'Very familiar',
            'Somewhat familiar',
            'Not familiar at all'
        ],
        label="Before today, how familiar were you with warning/information labels or watermarks on social media?",
        widget=widgets.RadioSelect
    )

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
        # required=True
    )

    # AI/SMP questions pre-treatment:
    smp_entertaining_pre = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label="I find the content on social media platforms entertaining",
    )

    smp_accuracy_pre = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label='I trust the accuracy of the content on social media platforms',
    )

    smp_enjoyment_pre = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label='I enjoy spending time on social media platforms',
    )

    smp_community_pre = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label='I feel part of a community on social media platforms',
    )

    smp_news_pre = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label='I get my news from social media platforms',
    )
    # from pew https://www.pewresearch.org/wp-content/uploads/sites/20/2024/10/SR_24.10.16_media-trust-topline.pdf
    image_accuracy_ai = models.StringField(blank=True)
    why_click_ai = models.LongStringField(
        label="Why did you click on that spot?",
        blank=False
    )
    why_click_real = models.LongStringField(
        label="Why did you click on that spot?",
        blank=False
    )
    image_claim_true_ai = models.StringField(blank=True)
    image_feelstrue_ai = models.StringField(blank=True)
    image_feelstrue_real = models.StringField(blank=True)
    image_confidence_ai = models.IntegerField(blank=True)
    image_accuracy_real = models.StringField(blank=True)
    image_confidence_real = models.IntegerField(blank=True)
    image_claim_true_real = models.StringField(blank=True)

    tweet_data = models.LongStringField()

# AI/SMP Questions Post-Treatment:
    llm_familiarity = models.StringField(
        choices=['Have not heard about them', 'Have heard a little about them but have not tried them out',
                 'Have heard about them and have tried them out',
                 'Use them sometimes in my work or personal life', 'Use them frequently in my work or personal life'],
        label="Before today, how familiar were you with large language models (LLMs), or artificial intelligence (AI) chatbots, like ChatGPT, Gemini, or Claude?",
        widget=widgets.RadioSelect,
        required=None
    )
    use_twitter = models.StringField(
        choices=["Several times a day", "About once a day", "A few days a week", "Every few weeks",
                 "Less often", "Never", "Don't know"],
        label="Twitter/X",
        widget=widgets.RadioSelect,
    )

    use_reddit = models.StringField(
        choices=["Several times a day", "About once a day", "A few days a week", "Every few weeks",
                 "Less often", "Never", "Don't know"],
        label="Reddit",
        widget=widgets.RadioSelect,
    )

    use_instagram = models.StringField(
        choices=["Several times a day", "About once a day", "A few days a week", "Every few weeks",
                 "Less often", "Never", "Don't know"],
        label=mark_safe("Instagram/<br>Threads"),
        widget=widgets.RadioSelect,
    )

    use_pinterest = models.StringField(
        choices=["Several times a day", "About once a day", "A few days a week", "Every few weeks",
                 "Less often", "Never", "Don't know"],
        label="Pinterest",
        widget=widgets.RadioSelect,
    )

    use_linkedin = models.StringField(
        choices=["Several times a day", "About once a day", "A few days a week", "Every few weeks",
                 "Less often", "Never", "Don't know"],
        label="LinkedIn",
        widget=widgets.RadioSelect,
    )

    use_facebook = models.StringField(
        choices=["Several times a day", "About once a day", "A few days a week", "Every few weeks",
                 "Less often", "Never", "Don't know"],
        label="Facebook",
        widget=widgets.RadioSelect,
    )

    use_youtube = models.StringField(
        choices=["Several times a day", "About once a day", "A few days a week", "Every few weeks",
                 "Less often", "Never", "Don't know"],
        label="YouTube",
        widget=widgets.RadioSelect,
    )

    use_tiktok = models.StringField(
        choices=["Several times a day", "About once a day", "A few days a week", "Every few weeks",
                 "Less often", "Never", "Don't know"],
        label="TikTok",
        widget=widgets.RadioSelect,
    )

    use_bluesky = models.StringField(
        choices=["Several times a day", "About once a day", "A few days a week", "Every few weeks",
                 "Less often", "Never", "Don't know"],
        label="Bluesky",
        widget=widgets.RadioSelect,
    )

    use_truthsocial = models.StringField(
        choices=["Several times a day", "About once a day", "A few days a week", "Every few weeks",
                 "Less often", "Never", "Don't know"],
        label="Truth Social",
        widget=widgets.RadioSelect,
    )

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
    trust_AI_company = models.StringField(
        choices=['A lot', 'Some', 'Not too much', 'Not at all', 'No opinion'],
        widget=widgets.RadioSelect,
        label='Companies that build artificial intelligence (AI) tools'
    )
    trust_actors_order = models.StringField(blank=True)

    trust_user = models.StringField(
        choices=['A lot', 'Some', 'Not too much', 'Not at all', 'No opinion'],
        widget=widgets.RadioSelect,
        label='Users who post content on social media platforms'
    )

    trust_smp = models.StringField(
        choices=['A lot', 'Some', 'Not too much', 'Not at all', 'No opinion'],
        widget=widgets.RadioSelect,
        label='Social media platforms'
    )

    trust_journalists_factcheckers = models.StringField(
        choices=['A lot', 'Some', 'Not too much', 'Not at all', 'No opinion'],
        widget=widgets.RadioSelect,
        label='Journalists or fact-checkers'
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
    understand_AI = models.LongStringField()

    consentdebrief = models.StringField(choices=['yes', 'no'])

# FUNCTIONS -----
def creating_session(subsession):
    # Read data and preprocess tweets
    df = read_feed(subsession.session.config['data_path'])
    tweets = preprocessing(df)

    # Convert 'doc_id' to string and strip whitespace once upfront
    df['doc_id'] = df['doc_id'].astype(str).str.strip()

    # Store dataframes in session vars so they can be accessed later
    subsession.session.vars['full_tweets_df'] = df
    subsession.session.vars['processed_tweets'] = tweets

    # Assign random vars to each player
    for player in subsession.get_players():
        # Randomly assign info treatment condition (50/50 split)
        player.participant.vars['show_info_treatment'] = random.random() < 0.5

        # Set default to False (will be updated if they see the page)
        player.shown_info_treatment = False

        order = ['AI', 'Real'] if random.random() < 0.5 else ['Real', 'AI']
        player.participant.vars['question_order'] = order
        player.participant.vars['first_question'] = order[0]
        player.participant.vars['second_question'] = order[1]

        # Generate and store SMP statements order
        smp_fields = ['smp_entertaining', 'smp_accuracy', 'smp_enjoyment', 'smp_community', 'smp_news']
        random.shuffle(smp_fields)
        player.participant.vars['smp_order'] = smp_fields

        # Generate and store SMP post statements order
        smp_post_fields = ['smp_entertaining_post', 'smp_accuracy_post', 'smp_enjoyment_post', 'smp_community_post',
                           'smp_news_post']
        random.shuffle(smp_post_fields)
        player.participant.vars['smp_post_order'] = smp_post_fields

        # Generate and store trust actors order
        trust_actors_fields = ['trust_AI_company', 'trust_user', 'trust_smp', 'trust_journalists_factcheckers']
        random.shuffle(trust_actors_fields)
        player.participant.vars['trust_actors_order'] = trust_actors_fields

        # Generate and store social media order
        social_media_fields = ['use_twitter', 'use_reddit', 'use_instagram', 'use_pinterest',
                               'use_linkedin', 'use_facebook', 'use_youtube', 'use_tiktok',
                               'use_bluesky', 'use_truthsocial']
        random.shuffle(social_media_fields)
        player.participant.vars['social_media_order'] = social_media_fields

        # Generate and store watermark statements order
        watermark_statements_fields = ['clarity_watermarks', 'informative_watermarks',
                                       'trustworthy_watermarks', 'biased_watermarks']
        random.shuffle(watermark_statements_fields)
        player.participant.vars['watermark_statements_order'] = watermark_statements_fields

        # Generate and store creates_watermarks options order
        creates_watermarks_options = ['AI company', 'social media user', 'social media platform',
                                      'journalists or factcheckers']
        random.shuffle(creates_watermarks_options)
        player.participant.vars['creates_watermarks_order'] = creates_watermarks_options

        # Mark that treatment has not been assigned yet
        player.participant.vars['treatment_assigned'] = False

def assign_treatment_posts(player):
    """Assign treatment and control posts AFTER party_id is collected, with blocking by party_id"""

    # Check if already assigned
    if player.participant.vars.get('treatment_assigned', False):
        print(f"Treatment already assigned for player {player.id_in_group}")
        return

    # Get the stored dataframes
    df = player.subsession.session.vars['full_tweets_df']
    tweets = player.subsession.session.vars['processed_tweets']

    print(f"Assigning treatment for player {player.id_in_group} with party_id: {player.party_id}")

    # Initialize blocking structures in session vars if not present
    if 'party_treatment_counters' not in player.session.vars:
        player.session.vars['party_treatment_counters'] = {}
    if 'party_watermark_counters' not in player.session.vars:
        player.session.vars['party_watermark_counters'] = {}

    party_id = player.party_id

    # Initialize counters for this party_id if not present
    if party_id not in player.session.vars['party_treatment_counters']:
        # Create shuffled list of treatment types for this party
        base_treatment_types = [
            'Negative Democrat',
            'Negative Republican',
            'Positive Democrat',
            'Positive Republican'
        ]

        # Create a large pool of treatments (2/3 realistic, 1/3 artistic)
        treatment_pool = []
        for _ in range(300):  # Make a pool of 1200 treatments (300 × 4 base types)
            for base_type in base_treatment_types:
                style = 'Artistic' if random.random() < 1 / 3 else 'Realistic'
                full_treatment = f"{base_type.split()[0]} {style} {base_type.split()[1]}"
                treatment_pool.append(full_treatment)

        random.shuffle(treatment_pool)
        player.session.vars['party_treatment_counters'][party_id] = {
            'pool': treatment_pool,
            'index': 0
        }

        if party_id not in player.session.vars['party_watermark_counters']:
            # Create shuffled list of watermarks for this party
            watermark_options = [
                "none", "fb_content_warning", "insta_content_warning",
                "cr_watermark", "cr_watermark_plus_label"
            ]

            # Create a large pool of watermarks
            watermark_pool = watermark_options * 240  # 1200 watermarks (240 × 5 options)
            random.shuffle(watermark_pool)
            player.session.vars['party_watermark_counters'][party_id] = {
                'pool': watermark_pool,
                'index': 0
            }

    # Get treatment type from the pool
    treatment_counter = player.session.vars['party_treatment_counters'][party_id]
    treatment_type = treatment_counter['pool'][treatment_counter['index']]
    treatment_counter['index'] += 1

    # Get watermark from the pool
    watermark_counter = player.session.vars['party_watermark_counters'][party_id]
    player.watermark_condition = watermark_counter['pool'][watermark_counter['index']]
    watermark_counter['index'] += 1

    print(f"  Assigned treatment_type: {treatment_type}")
    print(f"  Assigned watermark: {player.watermark_condition}")

    # Filter treatment and control posts
    all_treatment_types = [
        'Negative Artistic Democrat', 'Negative Artistic Republican',
        'Negative Realistic Democrat', 'Negative Realistic Republican',
        'Positive Artistic Democrat', 'Positive Artistic Republican',
        'Positive Realistic Democrat', 'Positive Realistic Republican'
    ]
    treatment_posts = tweets[tweets['treatment_type'].isin(all_treatment_types)]
    control_posts = tweets[~tweets['treatment_type'].isin(all_treatment_types)]

    if treatment_posts.empty:
        raise ValueError("No treatment posts found")

    # Control categories
    control_categories = ['sports', 'technology', 'entertainment', 'politics']

    selected_control_posts = []

    # Sample one treatment post
    selected_treatment_post = treatment_posts[treatment_posts['treatment_type'] == treatment_type].sample(n=1).copy()

    # Assign treatment post info to player
    assigned_image_id = str(selected_treatment_post['doc_id'].values[0]).strip()
    player.assigned_image_id = assigned_image_id

    # get AI image claim
    if 'claim_ai' in selected_treatment_post.columns:
        player.claim_ai = selected_treatment_post['claim_ai'].values[0]
        print(f"Player {player.id_in_group}: Assigned claim_ai = '{player.claim_ai}'")

    # Disclaimer assignment
    kamala_ids = {'101', '102', '105', '106', '109', '114'}
    donald_ids = {'103', '104', '107', '108', '111', '115', '120', '122', '126'}
    donald_taylor_ids = '116'
    andrew_ids = '117'
    donald_elon_ids = '125'
    charlie_ids = '123', '124'
    chuck_hakeem_ids = '121'
    chuck_ids = '119'
    zohran_ids = '118'

    if assigned_image_id in kamala_ids:
        player.disclaimer = "Kamala Harris"
    elif assigned_image_id in donald_ids:
        player.disclaimer = "Donald Trump"
    elif assigned_image_id in donald_taylor_ids:
        player.disclaimer = "Taylor Swift and Donald Trump"
    elif assigned_image_id in donald_elon_ids:
        player.disclaimer = "Donald Trump and Elon Musk"
    elif assigned_image_id in charlie_ids:
        player.disclaimer = "Charlie Kirk"
    elif assigned_image_id in chuck_hakeem_ids:
        player.disclaimer = "Chuck Schumer and Hakeem Jeffries"
    elif assigned_image_id in chuck_ids:
        player.disclaimer = "Chuck Schumer"
    elif assigned_image_id in zohran_ids:
        player.disclaimer = "Zohran Mamdani"
    elif assigned_image_id in andrew_ids:
        player.disclaimer = "Andrew Cuomo"
    else:
        player.disclaimer = ""

    feed_row = df[df['doc_id'] == assigned_image_id]
    player.feed_condition_row = feed_row.to_json(orient='records') if not feed_row.empty else None

    # Set watermark on treatment post
    selected_treatment_post['watermark'] = player.watermark_condition
    selected_treatment_post['watermark'] = selected_treatment_post['watermark'].str.strip()

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

                if 'claim_real' in selected_post.columns:
                    player.claim_real = selected_post['claim_real'].values[0]

                player.assigned_politics_id = str(selected_post['doc_id'].values[0]).strip()

                control_feed_row = df[df['doc_id'] == player.assigned_politics_id]
                if not control_feed_row.empty:
                    player.control_feed_condition_row = control_feed_row.to_json(orient='records')

                print(f"Player {player.id_in_group}: politics control doc_id = {player.assigned_politics_id}")
                print(f"Player {player.id_in_group}: claim_real = {player.claim_real}")

    # Combine treatment and control posts into DataFrame
    selected_control_df = pd.DataFrame(selected_control_posts)
    selected_posts_df = pd.concat([selected_treatment_post, selected_control_df], ignore_index=True)

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

    player.tweets_json = selected_posts_df.to_json(orient='records')
    # Assign shuffled posts DataFrame to participant.tweets
    player.participant.tweets = selected_posts_df

    # Mark as assigned
    player.participant.vars['treatment_assigned'] = True

    print(f"✅ Treatment assigned successfully for player {player.id_in_group}")
# make images visible
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
    df['user_followers'] = df['user_followers'].map('{:,.0f}'.format)

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

class AttentionCheck(Page):
    form_model = 'player'
    form_fields = ['prolific_id', 'attention_check']

class B_SMPsTrust(Page):
    form_model = 'player'
    form_fields = [
        'party_id',
        'use_twitter',
        'use_reddit',
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
        'color_check'
    ]

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.prolific_id = player.participant.label

        # Save the randomization orders
        if 'social_media_order' in player.participant.vars:
            player.social_media_order = json.dumps(player.participant.vars['social_media_order'])

        if 'smp_order' in player.participant.vars:
            player.smp_order = json.dumps(player.participant.vars['smp_order'])

        # assign treatment based on party_id
        assign_treatment_posts(player)

class C_FeedInstructions(Page):
    form_model = 'player'

class C_Feed(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        fields = ['likes_data', 'replies_data', 'touch_capability', 'device_type',
                  'retweets_data', 'watermark_hover_events', 'insta_uncover_clicks']  # Added insta_uncover_clicks
        if not player.session.config['topics'] & player.session.config['show_cta']:
            more_fields = ['scroll_sequence', 'viewport_data']
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

class D_DirectQuestions_AI_First(Page):
    form_model = 'player'
    form_fields = [
        'image_accuracy_ai',
        'image_confidence_ai',
        'click_x_ai',
        'click_y_ai',
        'why_click_ai',
        'image_claim_true_ai',
        'image_feelstrue_ai',
        'familiarity_ai',
    ]

    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('first_question') == 'AI'
    @staticmethod
    def vars_for_template(player):
        return {
            'claim_ai': player.claim_ai,
            'screenshot_treatment': player.screenshot_treatment
        }

    @staticmethod
    def before_next_page(player, timeout_happened):
        """Process form data and save participant vars"""

        # Copy first_question and question_order into Player for CSV export
        if 'first_question' in player.participant.vars:
            player.first_question = player.participant.vars['first_question']
        if 'question_order' in player.participant.vars:
            player.question_order = json.dumps(player.participant.vars['question_order'])

        # Process all form fields using existing method
        for field_name in ['why_click_ai', 'image_claim_true_ai',
                           'image_feelstrue_ai', 'image_confidence_ai',
                           'image_accuracy_ai', 'familiarity_ai']:
            new_val = player.field_maybe_none(field_name)
            if new_val and not getattr(player, field_name, None):
                setattr(player, field_name, new_val)
                print(f"Saved {field_name}: {new_val}")

        print("=== AI PAGE BEFORE_NEXT_PAGE COMPLETED ===")

class D_DirectQuestions_Real_First(Page):
    form_model = 'player'
    form_fields = [
        'click_x_real',
        'click_y_real',
        'image_accuracy_real',
        'image_confidence_real',
        'why_click_real',
        'image_claim_true_real',
        'image_feelstrue_real',
        'familiarity_real',
    ]

    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('first_question') == 'Real'

    @staticmethod
    def vars_for_template(player):
        return {
            'claim_real': player.claim_real,
            # If you also need the screenshot:
            'screenshot_control': player.screenshot_control
        }

    @staticmethod
    def before_next_page(player, timeout_happened):
        # Save values from participant.vars into Player fields for CSV export
        if 'first_question' in player.participant.vars:
            player.first_question = player.participant.vars['first_question']
        if 'question_order' in player.participant.vars:
            player.question_order = json.dumps(player.participant.vars['question_order'])

        # Debug: Print current field values
        print("=== FIELD VALUES AFTER FORM PROCESSING ===")
        for field_name in ['image_accuracy_real', 'image_confidence_real',
                           'image_claim_true_real']:
            value = getattr(player, field_name, 'NOT SET')
            print(f"{field_name}: {value}")
        print("=== END DEBUG ===")

class D_DirectQuestions_AI_Second(Page):
    form_model = 'player'
    form_fields = [
        'image_accuracy_ai',
        'image_confidence_ai',
        'click_x_ai',
        'click_y_ai',
        'why_click_ai',
        'image_claim_true_ai',
        'image_feelstrue_ai',
        'familiarity_ai',
    ]

    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('first_question') == 'Real'

    @staticmethod
    def vars_for_template(player):
        return {
            'claim_ai': player.claim_ai,
            'screenshot_treatment': player.screenshot_treatment
        }
    @staticmethod
    def before_next_page(player, timeout_happened):
        """Process form data and save participant vars"""

        # Copy first_question and question_order into Player for CSV export
        if 'first_question' in player.participant.vars:
            player.first_question = player.participant.vars['first_question']
        if 'question_order' in player.participant.vars:
            player.question_order = json.dumps(player.participant.vars['question_order'])

        # Process all form fields using existing method
        for field_name in ['why_click_ai', 'image_claim_true_ai',
                           'image_feelstrue_ai', 'image_confidence_ai',
                           'image_accuracy_ai', 'familiarity_ai']:
            new_val = player.field_maybe_none(field_name)
            if new_val and not getattr(player, field_name, None):
                setattr(player, field_name, new_val)
                print(f"Saved {field_name}: {new_val}")

        print("=== AI PAGE BEFORE_NEXT_PAGE COMPLETED ===")

class D_DirectQuestions_Real_Second(Page):
    form_model = 'player'
    form_fields = [
        'click_x_real',
        'click_y_real',
        'image_accuracy_real',
        'image_confidence_real',
        'why_click_real',
        'image_claim_true_real',
        'image_feelstrue_real',
        'familiarity_real',
    ]

    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('first_question') == 'AI'
    @staticmethod
    def vars_for_template(player):
        return {
            'claim_real': player.claim_real,
            # If you also need the screenshot:
            'screenshot_control': player.screenshot_control
        }

    @staticmethod
    def before_next_page(player, timeout_happened):
        # Save values from participant.vars into Player fields for CSV export
        if 'first_question' in player.participant.vars:
            player.first_question = player.participant.vars['first_question']
        if 'question_order' in player.participant.vars:
            player.question_order = json.dumps(player.participant.vars['question_order'])

        # Debug: Print current field values
        print("=== FIELD VALUES AFTER FORM PROCESSING ===")
        for field_name in ['image_accuracy_real', 'image_confidence_real',
                           'image_claim_true_real']:
            value = getattr(player, field_name, 'NOT SET')
            print(f"{field_name}: {value}")
        print("=== END DEBUG ===")

class H_Demographics(Page):
    form_model = 'player'
    form_fields = ["age", "gender", "state", "race", "education", "income"]


class MorePosts(Page):
    form_model = 'player'
    form_fields = [
        'moreposts_image_check_1',
        'moreposts_image_check_2',
        'moreposts_image_check_3',
        'moreposts_image_check_4',
        'moreposts_image_check_5',
    ]

    @staticmethod
    def vars_for_template(player: Player):
        # 1. Get the randomized dataframe from participant vars
        df = player.participant.tweets

        # 2. Extract the screenshot column based on the post type
        # In your assign_treatment_posts, 'treatment' rows have
        # player.screenshot_treatment, 'control' rows have screenshot_control.
        options = []
        for _, row in df.iterrows():
            if row['post_type'] == 'treatment':
                # Use the assigned treatment screenshot (with watermarks)
                img = player.screenshot_treatment
            else:
                # Use the standard control screenshot
                img = row.get('screenshot_control')

            if img:
                options.append(img)

        # 3. Limit to first 5 to match your 5 form fields
        options = options[:5]

        # 4. Save metadata for your records
        player.image_options_json = json.dumps(options)
        # It's better to use orient='records' to keep row order in JSON
        player.tweets_json = df.to_json(orient='records')

        return dict(image_options=options)

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

    @staticmethod
    def before_next_page(player, timeout_happened):
        # Save the randomization orders
        if 'watermark_statements_order' in player.participant.vars:
            player.watermark_statements_order = json.dumps(player.participant.vars['watermark_statements_order'])

        if 'creates_watermarks_order' in player.participant.vars:
            player.creates_watermarks_order = json.dumps(player.participant.vars['creates_watermarks_order'])

class G_AISMPQuestions(Page):
    form_model = "player"
    form_fields = ["llm_familiarity", "smp_entertaining_post", "smp_accuracy_post", "smp_enjoyment_post", "smp_community_post",
                   "smp_news_post", "distinguish_ability", "benefits_ai",
                   'trust_journalists_factcheckers', 'trust_smp', 'trust_user', 'trust_AI_company', 'watermark_familiarity']

    @staticmethod
    def before_next_page(player, timeout_happened):
        # Save the randomization orders
        if 'trust_actors_order' in player.participant.vars:
            player.trust_actors_order = json.dumps(player.participant.vars['trust_actors_order'])

        if 'smp_post_order' in player.participant.vars:
            player.smp_post_order = json.dumps(player.participant.vars['smp_post_order'])

class Info_Treatment(Page):
    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('show_info_treatment', False)

    @staticmethod
    def before_next_page(player, timeout_happened):
        # Record that they saw the info treatment
        player.shown_info_treatment = True

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
    AttentionCheck,
    B_SMPsTrust,
    C_FeedInstructions,
    C_Feed,
    D_DirectQuestions_Real_First,
    D_DirectQuestions_AI_First,
    D_DirectQuestions_Real_Second,
    D_DirectQuestions_AI_Second,
    MorePosts,
    F_Watermarks,
    G_AISMPQuestions,
    H_Demographics,
    Info_Treatment,
    H_Debrief,
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
        yield [session.code, participant.code, participant.label, p.id_in_group,
               p.watermark_condition, p.scroll_sequence, p.viewport_data, p.likes_data, p.replies_data, p.retweets_data]