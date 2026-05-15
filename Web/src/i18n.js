import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

import commonDe from './locales/common/de.json'
import commonEn from './locales/common/en.json'
import navigationDe from './locales/navigation/de.json'
import navigationEn from './locales/navigation/en.json'
import studyDe from './locales/study/de.json'
import studyEn from './locales/study/en.json'
import experimentDe from './locales/experiment/de.json'
import experimentEn from './locales/experiment/en.json'
import configurationDe from './locales/configuration/de.json'
import configurationEn from './locales/configuration/en.json'
import overviewDe from './locales/overview/de.json'
import overviewEn from './locales/overview/en.json'
import participantDe from './locales/participant/de.json'
import participantEn from './locales/participant/en.json'
import questionnaireDe from './locales/questionnaire/de.json'
import questionnaireEn from './locales/questionnaire/en.json'
import analysisDe from './locales/analysis/de.json'
import analysisEn from './locales/analysis/en.json'
import debugDe from './locales/debug/de.json'
import debugEn from './locales/debug/en.json'

i18n
  .use(initReactI18next)
  .init({
    lng: localStorage.getItem('lang') ?? 'de',
    fallbackLng: 'de',
    defaultNS: 'common',
    resources: {
      de: {
        common: commonDe,
        navigation: navigationDe,
        study: studyDe,
        experiment: experimentDe,
        configuration: configurationDe,
        overview: overviewDe,
        participant: participantDe,
        questionnaire: questionnaireDe,
        analysis: analysisDe,
        debug: debugDe,
      },
      en: {
        common: commonEn,
        navigation: navigationEn,
        study: studyEn,
        experiment: experimentEn,
        configuration: configurationEn,
        overview: overviewEn,
        participant: participantEn,
        questionnaire: questionnaireEn,
        analysis: analysisEn,
        debug: debugEn,
      },
    },
    interpolation: { escapeValue: false },
  })

export default i18n
