'user_id': hashed userID.
'bot_id': bot name.
'Aff_Pretest': favorability score pre-test
'Aff_Posttest': favorability score post-test
'Aff_Change': favorability score change
'version': version of the experiment.
'condition': which user group this bot belong?
'CUQ_1', 'CUQ_2R', 'CUQ_3', 'CUQ_4R', 'CUQ_5', 'CUQ_6R', 'CUQ_7', 'CUQ_8R', 'CUQ_9', 'CUQ_10R', 'CUQ_11', 'CUQ_12R', 'CUQ_13', 'CUQ_14R', 'CUQ_15', 'CUQ_16R': Chatbot Usability Questionaire original data.
'cuq_score_12': Calculated result for the first 12 CUQ questions.
'cuq_score_16': Calculated result for all CUQ questions.
'cuq_score_12_except_5_6': Calculated result for the first 12 CUQ questions expect question 5 and 6.
'ubBIG5_Exterior','ubBIG5_Affinity','ubBIG5_OpenExperience','ubBIG5_Responsible','ubBIG5_Neurotic': users' feeling on bots Big Five personality in a 10 point Likert scale.
'cost_time': How many seconds did the user use to evaluate this chat agent?
'openChatHistory_duration': How many seconds did the user use to review chat history when evaluating this chat agent?
'openChatHistory': did user open chat history when evaluating this chat agent?
'sofar_openChatHistory_duration': how many seconds did the user use to review chat history when evaluating this round?
'sofar_openChatHistory': did user open chat history when evaluating this round?
'total_openChatHistory_duration': finally, how many seconds did the user use to review chat history when evaluating this round?
'total_openChatHistory': finally, did the user review chat history when evaluating this round?
'tag_count': how many tag user tagged for this bot?
'tagged': did user tag this bot?
'total_tags': how many tag user use in this round?
'total_tagged': did the user tag in this round?
'u_gender': users' gender
'u_age': users' age
'att_style': users' attachment style.
'atts_is_1', 'atts_is_2', 'atts_is_3': Dummy variable, will be 1 if users' attachment style is 1, 2, or 3.
'u_Extraversion','u_Agreeableness','u_Conscientiousness','u_Neuroticism','u_Openness': Users' Big Five Personalities score.
'u_Extraversion_1','u_Extraversion_2','u_Extraversion_3','u_Extraversion_4','u_Extraversion_5','u_Extraversion_6','u_Extraversion_7','u_Extraversion_8','u_Agreeableness_1','u_Agreeableness_2','u_Agreeableness_3','u_Agreeableness_4','u_Agreeableness_5','u_Agreeableness_6','u_Agreeableness_7','u_Agreeableness_8','u_Agreeableness_9','u_Conscientiousness_1','u_Conscientiousness_2','u_Conscientiousness_3','u_Conscientiousness_4','u_Conscientiousness_5','u_Conscientiousness_6','u_Conscientiousness_7','u_Conscientiousness_8','u_Conscientiousness_9','u_Neuroticism_1','u_Neuroticism_2','u_Neuroticism_3','u_Neuroticism_4','u_Neuroticism_5','u_Neuroticism_6','u_Neuroticism_7','u_Neuroticism_8','u_Openness_1','u_Openness_2','u_Openness_3','u_Openness_4','u_Openness_5','u_Openness_6','u_Openness_7','u_Openness_8','u_Openness_9','u_Openness_10','inv_u_Neuroticism_1','inv_u_Neuroticism_2','inv_u_Neuroticism_3','inv_u_Neuroticism_4','inv_u_Neuroticism_5','inv_u_Neuroticism_6','inv_u_Neuroticism_7','inv_u_Neuroticism_8',: Users' Big Five personality by question from Big Five personality scale.
'u_Extraversion_sp2','u_Extraversion_sp3','u_Extraversion_sp4','u_Agreeableness_sp2','u_Agreeableness_sp3','u_Agreeableness_sp4','u_Conscientiousness_sp2','u_Conscientiousness_sp3','u_Conscientiousness_sp4','u_Neuroticism_sp2','u_Neuroticism_sp3','u_Neuroticism_sp4','u_Openness_sp2','u_Openness_sp3','u_Openness_sp4','u_Plasticity','u_Plasticity_sp2','u_Plasticity_sp3','u_Plasticity_sp4','u_Stability','u_Stability_sp2','u_Stability_sp3','u_Stability_sp4': Group label if we seperate users into 'n' groups by their personality.

'bot_desc': Bots' description
'bot_gender': Bots' gender
'b_Agreeableness','b_Openness','b_Neuroticism','b_Conscientiousness','b_Extroversion': Dummy variable, will be 1 if bots' prompt is 1.
'bb_Agreeableness','bb_Non-Agreeableness','bb_Openness','bb_Non-Openness','bb_Neuroticism','bb_Non-Neuroticism','bb_Conscientiousness','bb_Non-Conscientiousness','bb_Extroversion','bb_Non-Extroversion','b_is_Plasticity','b_Plasticity','b_is_Stability','b_Stability','is_HighRankGroup','is_HighRankGroup_v2',: some gorup when performing data analysis.

'big5_is_same': If user and bot belong to the same Big Five Personality Dimension.

The followings are the output of the model we used for analyzing the conversation. Please google the column name for further information about the model:

'dennlinger/bert-wiki-paragraphs',
'microsoft/DialogRPT-depth',
'microsoft/DialogRPT-width',
'microsoft/DialogRPT-updown',
'microsoft/DialogRPT-human-vs-rand',
'microsoft/DialogRPT-human-vs-machine',
'in_anger_j-hartmann/emotion-english-distilroberta-base',
'in_disgust_j-hartmann/emotion-english-distilroberta-base',
'in_fear_j-hartmann/emotion-english-distilroberta-base',
'in_joy_j-hartmann/emotion-english-distilroberta-base',
'in_neutral_j-hartmann/emotion-english-distilroberta-base',
'in_sadness_j-hartmann/emotion-english-distilroberta-base',
'in_surprise_j-hartmann/emotion-english-distilroberta-base',
'anger_j-hartmann/emotion-english-distilroberta-base',
'disgust_j-hartmann/emotion-english-distilroberta-base',
'fear_j-hartmann/emotion-english-distilroberta-base',
'joy_j-hartmann/emotion-english-distilroberta-base',
'neutral_j-hartmann/emotion-english-distilroberta-base',
'sadness_j-hartmann/emotion-english-distilroberta-base',
'surprise_j-hartmann/emotion-english-distilroberta-base',
'N_dennlinger/bert-wiki-paragraphs',
'N_microsoft/DialogRPT-depth',
'N_microsoft/DialogRPT-width',
'N_microsoft/DialogRPT-updown',
'N_microsoft/DialogRPT-human-vs-rand',
'N_microsoft/DialogRPT-human-vs-machine',
'N_anger_j-hartmann/emotion-english-distilroberta-base',
'N_disgust_j-hartmann/emotion-english-distilroberta-base',
'N_fear_j-hartmann/emotion-english-distilroberta-base',
'N_joy_j-hartmann/emotion-english-distilroberta-base',
'N_neutral_j-hartmann/emotion-english-distilroberta-base',
'N_sadness_j-hartmann/emotion-english-distilroberta-base',
'N_surprise_j-hartmann/emotion-english-distilroberta-base',
'in_anger_j-hartmann/emotion-english-roberta-large',
'in_disgust_j-hartmann/emotion-english-roberta-large',
'in_fear_j-hartmann/emotion-english-roberta-large',
'in_joy_j-hartmann/emotion-english-roberta-large',
'in_neutral_j-hartmann/emotion-english-roberta-large',
'in_sadness_j-hartmann/emotion-english-roberta-large',
'in_surprise_j-hartmann/emotion-english-roberta-large',
'anger_j-hartmann/emotion-english-roberta-large',
'disgust_j-hartmann/emotion-english-roberta-large',
'fear_j-hartmann/emotion-english-roberta-large',
'joy_j-hartmann/emotion-english-roberta-large',
'neutral_j-hartmann/emotion-english-roberta-large',
'sadness_j-hartmann/emotion-english-roberta-large',
'surprise_j-hartmann/emotion-english-roberta-large',
'N_anger_j-hartmann/emotion-english-roberta-large',
'N_disgust_j-hartmann/emotion-english-roberta-large',
'N_fear_j-hartmann/emotion-english-roberta-large',
'N_joy_j-hartmann/emotion-english-roberta-large',
'N_neutral_j-hartmann/emotion-english-roberta-large',
'N_sadness_j-hartmann/emotion-english-roberta-large',
'N_surprise_j-hartmann/emotion-english-roberta-large',
