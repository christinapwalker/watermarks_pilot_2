# DICE/tests.py
from otree.api import Bot
from DICE.pages import (
    A_Consent, B_SMPsTrust, C_FeedInstructions, C_Feed,
    E_Logistics_Early, D_ItemCountQuestions_First, D_DirectQuestions_Real_First,
    D_DirectQuestions_AI_Second_FeelTrue, D_DirectQuestions_AI_Second_DoesNotFeelTrue,
    D_DirectQuestions_AI_First, D_DirectQuestions_Real_Second_DoesNotFeelTrue,
    D_DirectQuestions_Real_Second_FeelTrue, D_ItemCountQuestions_Last,
    E_Logistics_After, MorePosts, F_Watermarks, G_AISMPQuestions,
    H_Demographics, H_Debrief, I_PostDebrief, EndSurvey
)

class PlayerBot(Bot):
    def play_round(self):
        # 1️⃣ Consent page
        yield A_Consent, dict(consent=True)  # replace 'consent' with actual field(s)

        # 2️⃣ Trust in social media posts
        yield B_SMPsTrust, dict(trust_rating=5)  # replace with actual fields

        # 3️⃣ Feed instructions and feed page
        yield C_FeedInstructions
        yield C_Feed

        # 4️⃣ Early logistics page
        yield E_Logistics_Early, dict(all_images=3, loading=4, interaction=2)  # replace with real fields

        # 5️⃣ Item count and direct questions (example)
        yield D_ItemCountQuestions_First, dict(accurate_all=3, confidence_accurate=4, share=True)
        yield D_DirectQuestions_Real_First, dict(real_question1=2, real_question2=3)

        # 6️⃣ AI-related direct questions
        yield D_DirectQuestions_AI_First, dict(ai_question1=4)
        yield D_DirectQuestions_AI_Second_FeelTrue, dict(feels_true_answer=5)
        yield D_DirectQuestions_AI_Second_DoesNotFeelTrue, dict(feels_not_true_answer=3)

        # 7️⃣ Real second questions
        yield D_DirectQuestions_Real_Second_FeelTrue, dict(feels_true_answer=5)
        yield D_DirectQuestions_Real_Second_DoesNotFeelTrue, dict(feels_not_true_answer=2)

        # 8️⃣ Last item count questions
        yield D_ItemCountQuestions_Last, dict(accurate_all=4, confidence_accurate=5, share=False)

        # 9️⃣ After logistics
        yield E_Logistics_After

        # 10️⃣ More posts
        yield MorePosts

        # 11️⃣ Watermarks
        yield F_Watermarks, dict(watermark_manipulation_check=True)

        # 12️⃣ AI & SMP questions
        yield G_AISMPQuestions

        # 13️⃣ Demographics
        yield H_Demographics, dict(age=30, gender='female', education='college')  # replace with real fields

        # 14️⃣ Debrief
        yield H_Debrief
        yield I_PostDebrief

        # 15️⃣ End survey / thank you
        yield EndSurvey
