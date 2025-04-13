import csv
import os
from typing import List, Dict, Any

from django.core.management import BaseCommand
from django.db import transaction

from questionnaire.models import EnablerEntity, IndicatorEntity, QuestionEntity, StatementEntity
from questionnaire.services.enabler import EnablerService
from questionnaire.services.explanation import ExplanationService
from questionnaire.services.indicator import IndicatorService
from questionnaire.services.question import QuestionService
from questionnaire.services.statement import StatementService
from questionnaire.services.sub_indicator import SubIndicatorService


class Command(BaseCommand):
    help = "Pre process assessment fixtures"

    def handle(self, *args, **options):
        file_path = 'data.csv'
        result = self.process_csv(file_path)
        # output_file = 'fixture.json'
        # full_path = os.path.join(os.path.dirname(__file__), output_file)
        # with open(full_path, 'w') as json_file:
        #     json.dump(result, json_file, indent=4)
        self.save_to_db(result)

    def process_csv(self, file_path):
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        enablers = []
        current_enabler = None
        current_indicator = None

        with open(full_path, mode='r') as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                enabler = row['Enabler'].strip() if row['Enabler'] else None
                indicator = row['Indicator'].strip() if row['Indicator'] else None
                indicator_weightage = row['Indicator Weightage'].strip('%') if row['Indicator Weightage'] else None
                sub_indicator_name = row['Sub Indicator'].strip() if row['Sub Indicator'] else None
                question = row['Question'].strip() if row['Question'] else None
                statement = row['Statement'].strip() if row['Statement'] else None
                explanation = row['Explanation'].strip() if row['Explanation'] else None
                sub_indicator_weightage = row['Weightage'].strip('%') if row['Weightage'] else None

                if enabler:
                    if current_enabler:
                        enablers.append(current_enabler)
                    current_enabler = {
                        'enabler': enabler.strip(),
                        'indicators': []
                    }

                if indicator:
                    name, definition = indicator.split(":")
                    current_indicator = {
                        'name': name.strip(),
                        'weight_age': float(indicator_weightage),
                        'definition': " ".join(definition.strip().split("\n")).replace("\u2019", "'"),
                        'sub_indicators': [],
                        "question": question.strip(),
                        "statement": statement.strip(),
                        "explanation": self.process_exlanations(explanation.strip())
                    }
                    current_enabler['indicators'].append(current_indicator)

                if sub_indicator_name and current_indicator:
                    name, definition = sub_indicator_name.split(":")
                    sub_indicator = {
                        'name': name.strip(),
                        'weight_age': float(sub_indicator_weightage),
                        "definition": " ".join(definition.strip().split("\n")).replace("\u2019", "'")
                    }
                    current_indicator['sub_indicators'].append(sub_indicator)

            # Append the last enabler
            if current_enabler:
                enablers.append(current_enabler)

        return enablers

    def process_exlanations(self, explanation: str) -> List[str]:
        lines = explanation.split('\n')
        return [line.split(': ', 1)[1] for line in lines]

    def save_to_db(self, data: List[Dict[str, Any]]):
        try:
            with transaction.atomic():
                for e_x in data:
                    en_n = e_x.get("enabler")
                    enabler = self.create_enabler(en_n)
                    for i_n in e_x.get("indicators"):
                        indicator = self.create_indicator(i_n, enabler)
                        question = self.create_question(i_n.get("question"), indicator)
                        self.create_statement(i_n.get("statement"), indicator)
                        self.create_sub_indcators(i_n.get("sub_indicators"), indicator)
                        self.create_explanations(i_n.get("explanation"), question)

        except Exception as e:
            print("Could not save to db: ", e)

    def create_enabler(self, enabler: str) -> EnablerEntity:
        if EnablerService.get_enablers_by_name(enabler) is None:
            return EnablerService.create_enabler(name=enabler)
        else:
            raise Exception("Enabler already exists")

    def create_indicator(self, ind_n: Dict[str, Any], en: EnablerEntity) -> IndicatorEntity:
        if IndicatorService.get_indicator_by_name(ind_n.get("name")) is None:
            return IndicatorService.create_indicator(
                name=ind_n.get("name"),
                definition=ind_n.get("definition"),
                weightage=ind_n.get("weight_age"),
                enabler=en,
                is_included=True
            )
        else:
            raise Exception("Indicator already exists")

    def create_question(self, question: str, i_n: IndicatorEntity) -> QuestionEntity:
        return QuestionService.create_question(
            question_text=question,
            indicator=i_n,
            is_included=True,
            score=10
        )

    def create_statement(self, statement: str, i_n: IndicatorEntity) -> StatementEntity:
        return StatementService.create_statement(
            statement_text=statement,
            indicator=i_n,
            is_included=True
        )

    def create_sub_indcators(self, indicators: List[Dict[str, Any]], i_n: IndicatorEntity):
        for s_in in indicators:
            SubIndicatorService.create_sub_indicator(
                indicator=i_n,
                name=s_in.get("name"),
                definition=s_in.get("definition"),
                weightage=s_in.get("weight_age"),
                is_included=True
            )

    def create_explanations(self, explanations: List[str], qs: QuestionEntity):
        for x in explanations:
            ExplanationService.create_explanation(
                question=qs,
                explanation=x
            )
