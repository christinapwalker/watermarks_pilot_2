from os import environ

SESSION_CONFIGS = [ # defining a session
    dict(
        name='Watermarks_Experiment',
        display_name="Watermarks Experiment",
        app_sequence=['DICE'],
        num_demo_participants=3
    )
]


# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0,
    title = '',
    full_name = '',
    eMail = '',
    survey_link = 'https://your-link-here.com',
    url_param = 'PROLIFIC_PID',
    briefing = '', # '<h5>This could be your briefing</h5><p>Use HTML syntax to format your content to your liking.</p>',
    data_path='DICE/static/data/tweets.csv', # 'https://raw.githubusercontent.com/Howquez/oFeeds/main/software/DICE/DICE/static/data/tweets.csv', #'DICE/DICE/data/tweets.csv',
    sort_by='datetime',
    condition_col='condition',
    topics = True,
    # use_browser_bots=True,
    # copy_text = '50M Jobseekers. <br><br> 150+ Job Boards. <br><br> One Click.',
    copy_text= '', # 'Happy<br>National<br>Fried Chicken<br>Day!',
    show_cta = False,
    cta_text = '', # 'Post Jobs Free',
    # landing_page = 'https://unisg.qualtrics.com/jfe/form/SV_0DnMoLpM0VxjhrM',
    search_term = '#Yosemite',
)



PARTICIPANT_FIELDS = ['tweets', 'finished']
SESSION_FIELDS = ['prolific_completion_url', 'completion_code']

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = 'devsecret123'  # ← Add this line
