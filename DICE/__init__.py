# Load packages
from otree.api import *
import pandas as pd
import numpy as np
import re
import os
import random
import httplib2
from itertools import cycle
from collections import defaultdict
from . import image_utils
import pytz
import json

# from otree.api import (
#     models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer, Currency as c, currency_range
# )
# from django.utils.translation import ugettext_lazy as _
# from django.template.loader import render_to_string


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
    creates_watermarks_other = models.StringField(blank=True)
    moreposts_image_check_1 = models.StringField(choices=['like', 'neutral', 'dislike'], blank=True)
    moreposts_image_check_2 = models.StringField(choices=['like', 'neutral', 'dislike'], blank=True)
    moreposts_image_check_3 = models.StringField(choices=['like', 'neutral', 'dislike'], blank=True)
    moreposts_image_check_4 = models.StringField(choices=['like', 'neutral', 'dislike'], blank=True)
    moreposts_image_check_5 = models.StringField(choices=['like', 'neutral', 'dislike'], blank=True)

    saw_own_claim_real = models.BooleanField()
    show_own_claim_ai = models.BooleanField()
    shown_claims_ai = models.LongStringField(blank=True)
    image_feelstrue_followup = models.LongStringField(blank=True, null=True)
    image_feelsnottrue_followup = models.LongStringField(blank=True, null=True)
    image_feelstrue = models.StringField(blank=True)
    image_feelsnottrue_answered = models.StringField()
    image_feelsnottrue_answered = models.BooleanField(initial=False)
    image_feelsnottrue_answered = models.BooleanField(initial=False)

    # ad_condition = models.StringField(doc='indicates the ad condition a player is randomly assigned to') delete?
    # Metadata variables:
    disclaimer = models.StringField(blank=True, null=True)
    page_sequence = models.StringField()
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
    image1 = models.IntegerField(doc='indicates the first tweet shown based on doc_id')
    image2 = models.IntegerField(doc='indicates the second tweet shown based on doc_id')
    image3 = models.IntegerField(doc='indicates the third tweet shown based on doc_id')
    image4 = models.IntegerField(doc='indicates the fourth tweet shown based on doc_id')
    image5 = models.IntegerField(doc='indicates the fifth tweet shown based on doc_id')
    # cta = models.BooleanField(doc='indicates whether CTA was clicked or not') is this the watermark?
    scroll_sequence = models.LongStringField(doc='tracks the sequence of feed items a participant scrolled through.')
    viewport_data = models.LongStringField(doc='tracks the time feed items were visible in a participants viewport.')
    likes_data = models.LongStringField(doc='tracks likes.', blank=True)
    replies_data = models.LongStringField(doc='tracks replies.', blank=True)
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
        widget=widgets.RadioSelectHorizontal,
        required=True
    )

    # AI/SMP questions pre-treatment:
    smp_trust_users_pre = models.StringField(
        choices=['Not at all', 'Slightly', 'Moderately', 'Very', 'Extremely'],
        widget=widgets.RadioSelect,
        label='I generally trust that users on social media platforms will post accurate information.'
    )

    smp_entertaining_pre = models.StringField(
        choices=['Strongly Disagee', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label="I find the content on the social media platforms I use to be entertaining."
    )

    smp_trust_execs_pre = models.StringField(
        choices=['Not at all', 'Slightly', 'Moderately', 'Very', 'Extremely'],
        widget=widgets.RadioSelect,
        label='I trust social media executives to ensure accurate information.'
    )
    smp_accuracy_pre = models.StringField(
        choices=['Strongly Disagee', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label='I trust the accuracy of the content on the social media platforms that I use.'
    )

    smp_enjoyment_pre = models.StringField(
        choices=['Strongly Disagee', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label='I enjoy spending time on the social media platforms that I use.'
    )

    smp_community_pre = models.StringField(
        choices=['Strongly Disagee', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label='I feel part of a community on the social media platforms I use.'
    )

    smp_news_pre = models.StringField(
        choices=['Strongly Disagee', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label='I get my news from the social media platforms I use.'
    )
    # How much, if at all, do you trust the information you get from... need to randomize order
    # from pew https://www.pewresearch.org/wp-content/uploads/sites/20/2024/10/SR_24.10.16_media-trust-topline.pdf


    # Assessment of All Images (item count questions):
    accurate_all = models.IntegerField(
        label="How many of the images on the previous social media page do you believe are accurate?",
        choices=list(range(0,6))
    )
    confidence_accurate = models.IntegerField(
        label="How confident are you in your assessment of accurate images?",
        choices=list(range(0,11))
    )
    aigen_all = models.IntegerField(
        label="How many of the images on the previous social media page do you believe are AI-generated?", # has to equal 5-accurate_all
        choices=list(range(0,6))
    )
    confidence_aigen = models.IntegerField(
        label="How confident are you in your assessment of AI-generated images?",
        choices=list(range(0,11))
    )
    share = models.IntegerField(
        label="How many of the posts on the social media page would you share?",
        choices=list(range(0,6))
    )
    # bot_check_1 = models.IntegerField(
    #     choices=[1, 7, 3, 13, -7],
    #     widget=widgets.RadioSelect,
    #     label="Please select the number three:")
    #

    # Assessment of Individual Images (Direct Questions):
    # Image 1
    image_accuracy_ai = models.StringField(
        label="Do you believe the image in the post above is accurate or AI-generated?",
        choices=[
            ('Accurate', 'Accurate'),
            ('AI-generated', 'AI-generated'),
            ('Unsure', 'Unsure'),
        ],
        widget=widgets.RadioSelect,
        blank=True,
    )
    image_claim_ai = models.IntegerField(
        label="Some possible interpretations of the post and image are included below. Please select the option that you think best represents the claim of the post and image.",
        choices=[
            (1, 'Placeholder 1'),
            (2, 'Placeholder 2'),
            (3, 'Placeholder 3'),
            (4, 'Placeholder 4'),
            (5, 'Placeholder 5'),
        ],
        widget=widgets.RadioSelect,
        blank=True,
    )
    image_claim_true_ai = models.StringField(
        label="To what extent do you think that [pipe text from option they chose above] is literally true?",
        choices=[
            ('It is true', 'It is true'),
            ('It is not true', 'It is not true'),
        ],
        widget=widgets.RadioSelect,
        blank=True,
    )
    image_feelstrue_ai = models.IntegerField(min=0, max=100, blank=True, null=True)
    image_feelstrue_binary_ai = models.StringField(
        choices=[
            ('Does not feel true', 'Does not feel true'),
            ('Feels true', 'Feels true'),
        ],
        blank=True,
    )
    image_feelstrue_binary_real = models.StringField(
        choices=[['Feels true', 'Feels true'], ['Does not feel true', 'Does not feel true']],
        widget=widgets.RadioSelect,
        label="Does the claim feel true?",
        blank=True
    )
    # image_feelstrue_ai = models.IntegerField(
    #     label="What do you think it means if something 'feels true'?",
    #     blank = True,
    #     required = None
    # )
    image_reason_ai = models.IntegerField(
        label="On the post above, please click on the part that makes you believe the image was {accurate/AI-generated}."
    )
    image_confidence_ai = models.IntegerField(blank=True)  # e.g., 0-10 scale from your slider

    claim_response_real = models.StringField(
        label = "Regardless if the image in the post is an accurate image or AI-generated, what claim do you believe the post is making?",
        blank = True,
        required = None
    )
    claim_response_ai = models.StringField(
        label="Regardless if the image in the post is an accurate image or AI-generated, what claim do you believe the post is making?",
        blank=True,
    )
    claim_accuracy_ai = models.IntegerField(
        label = "Regardless if the image in the post is a real image or not, do you believe the claim of the post is accurate?",
        choices=['Not at all', 'Slightly', 'Moderately', 'Very', 'Extremely'],
        widget=widgets.RadioSelect
    )

    # Image 2
    image_accuracy_real = models.StringField(
        choices=[['AI-generated', 'Yes'], ['Accurate', 'No']],
        widget=widgets.RadioSelect,
        label="Is the image AI-generated?"
    )

    image_reason_real = models.IntegerField(
        label="On the post above, please click on the part that makes you believe the image was {accurate/AI-generated}."
    )

    image_confidence_real = models.IntegerField(
        label="How confident are you in your assessment of AI-generated images?",
        choices=list(range(0,11))
    )
    claim_response_real = models.StringField(
        label="Regardless if the image in the post is an accurate image or AI-generated, what claim do you believe the post is making?",
        blank=True,
        required=None
    )
    image_claim_real = models.StringField(
        blank=True  # claim choices are dynamically added, so don't predefine choices
    )
    image_claim_true_real = models.StringField(
        choices=[['It is true', 'It is true'], ['It is not true', 'It is not true']],
        widget=widgets.RadioSelect,
        label="To what extent is the claim true?"
    )
    image_claim_feelstrue_real = models.IntegerField(
        label="Regardless of whether you think the claim of the post is literally true, to what extent do you think the post represents something that feels true about the world?",
        choices=['Does not feel true', 'Feels true'], widget=widgets.RadioSelect,
    )
    image_feelstrue_real = models.IntegerField(min=0, max=100, blank=True, null=True)

    claim_accuracy_real = models.IntegerField(
        label="Regardless if the image in the post is a real image or not, do you believe the claim of the post is accurate?",
        choices=['Not at all', 'Slightly', 'Moderately', 'Very', 'Extremely'],
        widget=widgets.RadioSelect
    )

    # AI/SMP questions pre-treatment:
    frequency_smps = models.StringField(
        choices=['Several times a day', 'About once a day', 'A few days a week', 'Every few weeks', 'Less often',
                 'Never', 'Don\'t know'],
        label="Thinking about social media sites, how often do you visit or use the following?",
        # from Pew, https://www.pewresearch.org/wp-content/uploads/sites/9/2015/01/SurveyQuestions.pdf
        # Thinking about the social networking sites you use....About how often do you visit or use [insert]? Severla times a day, about once a day, a few days a aweek, every few weeks or less often?
        widget=widgets.RadioSelect,
    required=None)
    # Several times a day, about once a day, a few days a week, every few weeks, less often, never, don't know.
    # randomized platforms: twitter, instagram, pinterest, linkedin, facebook, threads, tiktok, truth social, bluesky
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
        choices=[
            ['several_day', 'Several times a day'],
            ['once_day', 'About once a day'],
            ['few_week', 'A few days a week'],
            ['few_weeks', 'Every few weeks'],
            ['less_often', 'Less often'],
            ['never', 'Never'],
            ['dont_know', "Don't know"]
        ],
        label="Twitter/X",
        widget=widgets.RadioSelect
    )

    use_instagram = models.StringField(
        choices=[
            ['several_day', 'Several times a day'],
            ['once_day', 'About once a day'],
            ['few_week', 'A few days a week'],
            ['few_weeks', 'Every few weeks'],
            ['less_often', 'Less often'],
            ['never', 'Never'],
            ['dont_know', "Don't know"]
        ],
        label="Instagram/Threads",
        widget=widgets.RadioSelect
    )

    use_pinterest = models.StringField(
        choices=[
            ['several_day', 'Several times a day'],
            ['once_day', 'About once a day'],
            ['few_week', 'A few days a week'],
            ['few_weeks', 'Every few weeks'],
            ['less_often', 'Less often'],
            ['never', 'Never'],
            ['dont_know', "Don't know"]
        ],
        label="Pinterest",
        widget=widgets.RadioSelect
    )

    use_linkedin = models.StringField(
        choices=[
            ['several_day', 'Several times a day'],
            ['once_day', 'About once a day'],
            ['few_week', 'A few days a week'],
            ['few_weeks', 'Every few weeks'],
            ['less_often', 'Less often'],
            ['never', 'Never'],
            ['dont_know', "Don't know"]
        ],
        label="LinkedIn",
        widget=widgets.RadioSelect
    )

    use_facebook = models.StringField(
        choices=[
            ['several_day', 'Several times a day'],
            ['once_day', 'About once a day'],
            ['few_week', 'A few days a week'],
            ['few_weeks', 'Every few weeks'],
            ['less_often', 'Less often'],
            ['never', 'Never'],
            ['dont_know', "Don't know"]
        ],
        label="Facebook",
        widget=widgets.RadioSelect
    )

    use_youtube = models.StringField(
        choices=[
            ['several_day', 'Several times a day'],
            ['once_day', 'About once a day'],
            ['few_week', 'A few days a week'],
            ['few_weeks', 'Every few weeks'],
            ['less_often', 'Less often'],
            ['never', 'Never'],
            ['dont_know', "Don't know"]
        ],
        label="YouTube",
        widget=widgets.RadioSelect
    )

    use_tiktok = models.StringField(
        choices=[
            ['several_day', 'Several times a day'],
            ['once_day', 'About once a day'],
            ['few_week', 'A few days a week'],
            ['few_weeks', 'Every few weeks'],
            ['less_often', 'Less often'],
            ['never', 'Never'],
            ['dont_know', "Don't know"]
        ],
        label="TikTok",
        widget=widgets.RadioSelect
    )

    use_bluesky = models.StringField(
        choices=[
            ['several_day', 'Several times a day'],
            ['once_day', 'About once a day'],
            ['few_week', 'A few days a week'],
            ['few_weeks', 'Every few weeks'],
            ['less_often', 'Less often'],
            ['never', 'Never'],
            ['dont_know', "Don't know"]
        ],
        label="Bluesky",
        widget=widgets.RadioSelect
    )

    use_truthsocial = models.StringField(
        choices=[
            ['several_day', 'Several times a day'],
            ['once_day', 'About once a day'],
            ['few_week', 'A few days a week'],
            ['few_weeks', 'Every few weeks'],
            ['less_often', 'Less often'],
            ['never', 'Never'],
            ['dont_know', "Don't know"]
        ],
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
        label="National News Organizations",
        widget=widgets.RadioSelect)
    trust_localnews_posttreatment = models.StringField(
        choices=[
            ['alot', 'A lot'],
            ['some', 'Some'],
            ['not_too_much', 'Not too much'],
            ['not_at_all', 'Not at all'],
            ['no_opinion', 'No opinion']
        ],
        label="Local News Organizations",
        widget=widgets.RadioSelect)
    trust_friendsfamily_posttreatment = models.StringField(
        choices=[
            ['alot', 'A lot'],
            ['some', 'Some'],
            ['not_too_much', 'Not too much'],
            ['not_at_all', 'Not at all'],
            ['no_opinion', 'No opinion']
        ],
        label="Friends and Family",
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
        choices=['A lot', 'Some', 'Not too much', 'Not at all',
                 'Do not use'],
        label='Thinking about society generally, the benefits of artificial intelligence (AI) outweigh the risks.',
        widget=widgets.RadioSelect)

    distinguish_ability = models.StringField(
        choices=['A lot', 'Some', 'Not too much', 'Not at all',
                 'Do not use'],
        label='I feel confident in my ability to distinguish real from AI-generated images.',
        widget=widgets.RadioSelect)
    smp_trust_users_post = models.StringField(
        choices=['Not at all', 'Slightly', 'Moderately', 'Very', 'Extremely'],
        widget=widgets.RadioSelect,
        label='I generally trust that users on social media platforms will post accurate information.'
    )
    smp_trust_execs_post = models.StringField(
        choices=['Not at all', 'Slightly', 'Moderately', 'Very', 'Extremely'],
        widget=widgets.RadioSelect,
        label='I trust social media executives to ensure accurate information.'
    )
    smp_accuracy_post = models.StringField(
        choices=[
            ['not_at_all', 'Not at all'],
            ['slightly', 'Slightly'],
            ['moderately', 'Moderately'],
            ['very', 'Very'],
            ['extremely', 'Extremely']
        ],
        widget=widgets.RadioSelect,
        label='I trust the accuracy of content on social media platforms that I use.'
    )

    smp_entertaining_post = models.StringField(
        choices=['Strongly Disagee', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label="I find the content on the social media platforms I use to be entertaining."
    )

    smp_trust_execs_post = models.StringField(
        choices=['Not at all', 'Slightly', 'Moderately', 'Very', 'Extremely'],
        widget=widgets.RadioSelect,
        label='I trust social media executives to ensure accurate information.'
    )
    smp_accuracy_post = models.StringField(
        choices=['Strongly Disagee', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label='I trust the accuracy of the content on the social media platforms that I use.'
    )

    smp_enjoyment_post = models.StringField(
        choices=['Strongly Disagee', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label='I enjoy spending time on the social media platforms that I use.'
    )

    smp_community_post = models.StringField(
        choices=['Strongly Disagee', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label='I feel part of a community on the social media platforms I use.'
    )

    smp_news_post = models.StringField(
        choices=['Strongly Disagee', 'Disagree', 'Neither Agree Nor Disagree', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelect,
        label='I get my news from the social media platforms I use.'
    )
    benefits_understanding_watermarks = models.IntegerField(min=1, max=5)


    # Demographics post-treatment:
    age = models.IntegerField(
        choices=list(range(18, 100)),
        label="How old are you?"
    )
    gender = models.StringField(
        label="What is your gender?",
        choices=[
            [1, 'A man'],
            [2, "A woman"],
            [3, "Non-binary"],
            [4, "Another gender"]
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
        choices=['White/Caucasian', 'African American', 'Hispanic', 'Native American', 'Asian', 'Pacific Islander',
                 'Other'],
        label="What is your race?",
        required=None
    )

    education = models.StringField(
        choices=['Less than a high school diploma', 'High school diploma/GED', 'Some college (no degree)',
                 '2-year college degree', '4-year college degree', 'Graduate degree'],
        widget=widgets.RadioSelect,
        label="What is the highest level of education that you have completed?",
        required=None
    )
    income = models.StringField(
        choices=['$0 - $24,999', '$25,000 - $49,999', '$50,000 - 74,999', '$75,000 - $99,999', '$100,000 - $149,999',
                 '$150,000 - $199,999', '$200,000+'],
        widget=widgets.RadioSelect,
        label="What is your combined household income?",
        required=None
    )

    # Logistics Questions:
    # all_images = models.IntegerField(
    #     choices=list(range(0, 10)),
    #     label="How many images did you see on the previous simulated social media page?",
    #     widget=widgets.RadioSelect
    # )
    all_images = models.IntegerField(
        choices=[(i, str(i)) for i in range(11)],
        widget=widgets.RadioSelect
    )
    loading = models.IntegerField(
        label="Did the images load quickly enough for you on the previous social media page?",
        choices=[(1, 'Yes'), (2, 'No')],
        widget=widgets.RadioSelect
    )
    # interaction = models.IntegerField(
    #     label="Were you able to interact with the posts (like, repost, or reply) on the previous social media page?",
    #     choices=[(1, 'Yes, I tried and was able to interact.'), (2, 'No, I tried but could not interact.'), (3, 'I did not try to interact.'), (4, 'Not Sure/Don\'t Remember')],
    #     widget=widgets.RadioSelect
    # )
    interaction = models.IntegerField(
        choices=[
            (1, 'Yes, I tried and was able to interact.'),
            (2, 'No, I tried but could not interact.'),
            (3, 'I did not try to interact.'),
            (4, "Not sure/Don't remember")
        ],
        widget=widgets.RadioSelect
    )
    study_topic = models.StringField(
        label="What do you believe this research study is about? That is, what is the purpose of this study?"
    )
    # political_content = models.IntegerField(
    #     min=0, max=10, label = "In your opinion, how many of the images on the previous social media page contained political content?"
    # )
    political_content = models.IntegerField(
        choices=[(i, str(i)) for i in range(11)],
        widget=widgets.RadioSelect
    )
    # watermark_familiarity = models.IntegerField(
    #     label="Before today, how familiar were you with watermarks or warning labels on social media?",
    #     widget=widgets.RadioSelect,
    #     choices=[(1, 'Very Familiar'), (2, 'Somewhat Familiar'), (3, "Not Familiar At All")],
    # )
    watermark_familiarity = models.IntegerField(
        choices=[
            (1, 'Very familiar'),
            (2, 'Somewhat familiar'),
            (3, 'Not familiar at all'),
        ],
        widget=widgets.RadioSelect
    )
    # watermark_manipulation_check = models.IntegerField(
    #     label="If you recall, did any of the images on the previous social media page have a watermark, label, or content warning?",
    #     choices=[(1, 'Yes'), (2, 'No'), (3, 'Not Sure')],
    #     widget=widgets.RadioSelect
    #     # choices= Select from a list of images or “Not sure/I don’t remember”
    # )
    watermark_manipulation_check = models.IntegerField(
        choices=[
            (1, 'Yes'),
            (2, 'No'),
            (3, 'Not sure')
        ],
        widget=widgets.RadioSelect
    )
    # watermark_image_check = models.LongStringField(
    #     label="If you recall, which image(s) had a watermark, label, or content warning?"
    # )
    watermark_image_check = models.LongStringField(blank=True)
    moreposts_image_check = models.LongStringField(blank=True)

    ethics_influence_political_prefs = models.IntegerField(
        label = 'Move the slider below to indicate to what extent do you believe the study will influence your political preferences:',
        min=1, max=5
    )
    political_influence = models.IntegerField(
        min=1, max=5, label ="Move the slider below to indicate to what extent this study helped you understand watermarks:"
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

    creates_watermarks_other = models.StringField(blank=True)


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

    # Calculate block size for groups (optional, you don't seem to use it after)
    min_group_size = min(len(group) for group in party_id_groups.values())

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

            # Assign random watermark condition
            player.watermark_condition = random.choice(watermark_options)
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
    urls = re.findall("(?P<url>https?://[\S]+)", str(text))
    if urls:
        return urls[0]
    return None

# check urls
h = httplib2.Http()

def check_url_exists(url):
    try:
        resp = h.request(url, 'HEAD')
        return int(resp[0]['status']) < 400
    except Exception:
        return False




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



def create_redirect(player):
    if player.participant.label:
        link = player.session.config['survey_link'] + '?' + player.session.config['url_param'] + '=' + player.participant.label
    else:
        link = player.session.config['survey_link'] + '?' + player.session.config['url_param'] + '=' + player.participant.code

    completion_code = None

    # if 'prolific_completion_url' in player.session.config and player.session.config['prolific_completion_url'] is not None:
        # completion_code = player.session.config['prolific_completion_url'][-8:]

    if 'completion_code' in player.session.vars:
        if player.session.vars['completion_code'] is not None:
            link = link + '&' + 'cc=' + player.session.vars['completion_code']

    return link





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

    # form_fields = ["party_id", "smp_entertaining_pre", "smp_accuracy_pre", "smp_enjoyment_pre", "smp_community_pre",
    #                "smp_news_pre", "use_twitter", "use_instagram", "use_pinterest", "use_linkedin", "use_facebook",
    #                "use_youtube", "use_tiktok", "use_bluesky", "use_truthsocial"]
    #




class C_FeedInstructions(Page):
    form_model = 'player'


class C_Feed(Page):
    form_model = 'player'

    @staticmethod

    def get_form_fields(player: Player):
        fields =  ['likes_data', 'replies_data', 'touch_capability', 'device_type']

        if not player.session.config['topics'] & player.session.config['show_cta']:
            more_fields =  ['scroll_sequence', 'viewport_data'] # , 'cta']
        else:
            more_fields =  ['scroll_sequence', 'viewport_data']

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

        # ✅ Existing prolific URL logic
        player.participant.finished = True
        if 'prolific_completion_url' in player.session.vars:
            if player.session.vars['prolific_completion_url'] is not None:
                if 'completion_code' in player.session.vars:
                    if player.session.vars['completion_code'] is not None:
                        player.session.vars[
                            'prolific_completion_url'] = 'https://app.prolific.com/submissions/complete?cc=' + \
                                                         player.session.vars['completion_code']
                    else:
                        player.session.vars['prolific_completion_url'] = 'https://app.prolific.com/submissions/complete'
                else:
                    player.session.vars['prolific_completion_url'] = 'https://app.prolific.com/submissions/complete'
            else:
                player.session.vars['prolific_completion_url'] = 'NA'
        else:
            player.session.vars['prolific_completion_url'] = 'NA'


class D_ItemCountQuestions_First(Page):
    form_model = 'player'
    form_fields = ['accurate_all', 'confidence_accurate', 'share']

    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('itemcount_first', False)

class D_ItemCountQuestions_Last(Page):
    form_model = 'player'
    form_fields = ['accurate_all', 'confidence_accurate', 'share']
    @staticmethod
    def is_displayed(player):
        return not player.participant.vars.get('itemcount_first', False)

class D_DirectQuestions_AI_First(Page):
    form_model = 'player'

    form_fields = [
        'click_x_ai',
        'click_y_ai',
        'image_feelstrue_followup',  # make sure these exist in Player
        'image_feelsnottrue_followup',
        'image_claim_ai',
        'image_accuracy_ai',
        'image_confidence_ai',
        'claim_response_ai',
        'image_claim_true_ai',
        'image_feelstrue_ai',
        'image_feelstrue_binary_ai',
    ]

    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('first_question') == 'AI'

    @staticmethod
    def vars_for_template(player):
        row_data = json.loads(player.feed_condition_row)[0]

        claims = [row_data[f'Claim {i}'] for i in range(1, 6)
                  if f'Claim {i}' in row_data and pd.notna(row_data[f'Claim {i}'])]

        # Randomly decide whether to show their own claim
        show_own = random.choice([True, False])
        player.participant.vars['show_own_claim_ai'] = show_own
        player.show_own_claim_ai = show_own  # ✅ Save to Player field

        # Save the list of claims shown
        player.shown_claims_ai = json.dumps(claims)

        return dict(
            claim_choices_ai=list(enumerate(claims, start=1)),
            show_slider=random.choice([True, False]),
            show_own_claim_ai=show_own,
        )


class D_DirectQuestions_Real_First(Page):
    form_model = 'player'

    form_fields = [
        'click_x_real',
        'click_y_real',
        'image_feelstrue_followup',
        'image_feelsnottrue_followup',
        'image_claim_real',
        'image_feelstrue_real',
        'image_feelstrue_binary_real',
        'saw_own_claim_real',
    ]

    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('first_question') == 'Real'

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

        claims = [row_data_real[f'Claim {i}'] for i in range(1, 6)
                  if f'Claim {i}' in row_data_real and pd.notna(row_data_real[f'Claim {i}'])]

        player.participant.vars['show_own_claim_real'] = random.choice([True, False])

        return dict(
            claim_choices_real=list(enumerate(claims, start=1)),
            show_slider_real=random.choice([True, False]),
            show_own_claim_real=player.participant.vars['show_own_claim_real'],
        )


class D_DirectQuestions_AI_Second_FeelTrue(Page):
    form_model = 'player'
    form_fields = ['click_x_ai', 'click_y_ai', 'image_claim_ai', 'image_feelstrue_followup', 'image_accuracy_ai',
                   'image_confidence_ai', 'claim_response_ai', 'image_claim_ai', 'image_claim_true_ai',
                   'image_feelstrue', 'image_feelstrue_binary_ai', 'image_feelstrue_followup']

    @staticmethod
    def is_displayed(player):

        # feel_true_binary = player.field_maybe_none('image_feelstrue_binary') or ''
        # feel_true_real = player.field_maybe_none('image_feelstrue_real') or 0

        return (
                player.participant.vars.get('second_question') == 'AI' and
                # (
                #         feel_true_binary == 'Feels true' or
                #         feel_true_real >= 50
                # ) and
                (player.field_maybe_none('image_feelstrue_followup') in [None, ''])
        )

    @staticmethod
    def vars_for_template(player):
        row_data = json.loads(player.feed_condition_row)[0]

        claims = [
            row_data[f'Claim {i}'] for i in range(1, 6)
            if f'Claim {i}' in row_data and pd.notna(row_data[f'Claim {i}'])
        ]

        player.participant.vars['show_own_claim_ai'] = random.choice([True, False])

        return dict(
            claim_choices_ai=list(enumerate(claims, start=1)),
            show_slider=random.choice([True, False]),
            show_own_claim_ai=player.participant.vars['show_own_claim_ai'],
        )

class D_DirectQuestions_AI_Second_DoesNotFeelTrue(Page):
    form_model = 'player'
    form_fields = ['click_x_ai', 'click_y_ai', 'image_claim_ai', 'image_feelsnottrue_followup']

    @staticmethod
    def is_displayed(player):

        return (
            player.participant.vars.get('second_question') == 'AI' and

            (player.field_maybe_none('image_feelsnottrue_followup') in [None, ''])
        )
    @staticmethod
    def vars_for_template(player):
        row_data = json.loads(player.feed_condition_row)[0]

        claims = [
            row_data[f'Claim {i}'] for i in range(1, 6)
            if f'Claim {i}' in row_data and pd.notna(row_data[f'Claim {i}'])
        ]

        player.participant.vars['show_own_claim_ai'] = random.choice([True, False])

        return dict(
            claim_choices_ai=list(enumerate(claims, start=1)),
            show_slider=random.choice([True, False]),
            show_own_claim_ai=player.participant.vars['show_own_claim_ai'],
        )


# class D_DirectQuestions_Real_Second(Page):
#     form_model = 'player'
#     form_fields = [
#         'click_x_real',
#         'click_y_real',
#         'image_feelstrue_followup',       # make sure these exist in Player
#         'image_feelsnottrue_followup',
#     ]
#
#     @staticmethod
#     def is_displayed(player):
#         return player.participant.vars.get('second_question') == 'Real'
#
#     @staticmethod
#     def vars_for_template(player):
#
#
#         row_data_real = json.loads(player.control_feed_condition_row)[0]
#
#         claims = [row_data_real[f'Claim {i}'] for i in range(1, 6)
#                   if f'Claim {i}' in row_data_real and pd.notna(row_data_real[f'Claim {i}'])]
#
#         player.participant.vars['show_own_claim_real'] = random.choice([True, False])
#
#         return dict(
#             claim_choices_real=list(enumerate(claims, start=1)),
#             show_slider_real=random.choice([True, False]),
#             show_own_claim_real=player.participant.vars['show_own_claim_real'],
#         )


class D_DirectQuestions_Real_Second_FeelTrue(Page):
    form_model = 'player'
    form_fields = [
        'click_x_real',
        'click_y_real',
        'image_feelstrue_followup',  # make sure these exist in Player
        'image_feelsnottrue_followup',
        'image_claim_real',
        'image_accuracy_real',
        'image_confidence_real',
        'claim_response_real',
        'image_claim_true_real',
        'image_feelstrue_real',
        'image_feelstrue_binary_real',
    ]
    @staticmethod
    def error_message(player, values):
        if values.get('click_x_real') in [None, ''] or values.get('click_y_real') in [None, '']:
            return "Please click on the image to indicate what influenced your decision."

    @staticmethod
    def is_displayed(player):
        return (
                player.participant.vars.get('second_question') == 'Real' and
                (player.field_maybe_none('image_feelstrue_real') in [None, ''])
        )
    @staticmethod
    def vars_for_template(player):
        row_data = json.loads(player.control_feed_condition_row)[0]


        claims = [
            row_data[f'Claim {i}'] for i in range(1, 6)
            if f'Claim {i}' in row_data and pd.notna(row_data[f'Claim {i}'])
        ]
        player.participant.vars['show_own_claim_real'] = random.choice([True, False])
        return dict(
            claim_choices_real=list(enumerate(claims, start=1)),
            show_slider_real=random.choice([True, False]),
            show_own_claim_real=player.participant.vars['show_own_claim_real'],
        )

class D_DirectQuestions_Real_Second_DoesNotFeelTrue(Page):
    form_model = 'player'
    form_fields = ['click_x_real', 'click_y_real', 'image_claim_real', 'image_feelsnottrue_followup']
    @staticmethod
    def is_displayed(player):
        return (
            player.participant.vars.get('second_question') == 'Real' and
            (player.field_maybe_none('image_feelsnottrue_followup') in [None, ''])
        )
    @staticmethod
    def vars_for_template(player):
        row_data = json.loads(player.control_feed_condition_row)[0]
        claims = [
            row_data[f'Claim {i}'] for i in range(1, 6)
            if f'Claim {i}' in row_data and pd.notna(row_data[f'Claim {i}'])
        ]
        player.participant.vars['show_own_claim_real'] = random.choice([True, False])
        return dict(
            claim_choices_real=list(enumerate(claims, start=1)),
            show_slider=random.choice([True, False]),
            show_own_claim_real=player.participant.vars['show_own_claim_real'],
        )
class H_Demographics(Page):
    form_model = 'player'
    form_fields = ["age", "gender", "state", "race", "education", "income"]

class F_SMPPostSurvey(Page):
    def vars_for_template(player: Player):
        return {
            'platforms': C.PLATFORMS
        }

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

    # def before_next_page(self):
    #     # Example: get from form or participant vars or somewhere
    #     self.player.watermark_image_check = self.player.participant.vars.get('watermark_check', '')
    #     # or assign from a form field
    #     # self.player.watermark_image_check = self.player.some_form_field

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
                   "trust_instagram_posttreatment", "trust_nationalnews_posttreatment", "trust_localnews_posttreatment", "trust_friendsfamily_posttreatment",
                   "trust_pinterest_posttreatment", "trust_linkedin_posttreatment", "trust_facebook_posttreatment",
                   "trust_youtube_posttreatment","trust_tiktok_posttreatment", "trust_bluesky_posttreatment","trust_truthsocial_posttreatment",
                   "trust_acquaintances_posttreatment", "smp_entertaining_post", "smp_accuracy_post",
                   "smp_enjoyment_post", "smp_community_post", "smp_news_post", "distinguish_ability", "benefits_ai"]

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

    def error_message(player, values):
        user_input = values.get('understand_AI', '').strip()
        if not H_Debrief._looks_ok(user_input, player.disclaimer):
            return "Please re-type the sentence acknowledging that the image is AI-generated."

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
    pass

page_sequence = [
    A_Consent,
    B_SMPsTrust,
    C_FeedInstructions,
    C_Feed,
    E_Logistics_Early,
    D_ItemCountQuestions_First,         # shows only if itemcount_first = True
    D_DirectQuestions_AI_First,
    D_DirectQuestions_Real_First,
    D_DirectQuestions_AI_Second_FeelTrue,
    D_DirectQuestions_AI_Second_DoesNotFeelTrue,
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
           'scroll_sequence', 'item_dwell_time', 'likes', 'replies']
    for p in players:
        participant = p.participant
        session = p.session
        yield [session.code, participant.code, participant.label, p.id_in_group, p.feed_condition, p.sequence,
               p.watermark_condition, p.scroll_sequence, p.viewport_data, p.likes_data, p.replies_data]

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
