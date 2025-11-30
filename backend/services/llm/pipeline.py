import os
import instructor
from openai import AsyncOpenAI
from typing import Optional, List
from pydantic import BaseModel
from schemas.analysis import LegislationAnalysisResponse, Impact
from services.research.zai import ZaiResearchService, ResearchPackage
import logging

logger = logging.getLogger(__name__)

class ReviewCritique(BaseModel):
    passed: bool
    critique: str
    missing_impacts: List[str]
    factual_errors: List[str]
    citation_issues: List[str]

class DualModelAnalyzer:
    def __init__(self):
        # Generator: x-ai/grok-4.1-fast (via OpenRouter)
        self.gen_client = instructor.from_openai(
            AsyncOpenAI(
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1",
            )
        )
        self.gen_model = "x-ai/grok-beta" # Using beta as proxy for 4.1-fast if not avail
        
        # Reviewer: glm-4.6 (via Z.ai or OpenRouter if Z.ai not standard OpenAI compat)
        # Assuming Z.ai provides an OpenAI-compatible endpoint or we use OpenRouter for it too
        self.review_client = instructor.from_openai(
            AsyncOpenAI(
                api_key=os.getenv("ZAI_API_KEY") or os.getenv("OPENROUTER_API_KEY"),
                base_url="https://api.z.ai/v1" if os.getenv("ZAI_API_KEY") else "https://openrouter.ai/api/v1",
            )
        )
        self.review_model = "glm-4" # Mapping to available model
        
        self.researcher = ZaiResearchService()

    async def analyze(self, bill_text: str, bill_number: str, jurisdiction: str) -> LegislationAnalysisResponse:
        """
        Full analysis pipeline:
        1. Exhaustive Research (Z.ai)
        2. Initial Generation (Grok)
        3. Review & Critique (GLM)
        4. Refinement (Grok)
        """
        logger.info(f"Starting dual-model analysis for {bill_number}")
        
        # 1. Research Phase
        research_package = await self.researcher.search_exhaustively(bill_text, bill_number)
        
        # 2. Generation Phase
        draft_analysis = await self._generate_draft(bill_text, bill_number, jurisdiction, research_package)
        
        # 3. Review Phase
        critique = await self._review_draft(bill_text, draft_analysis, research_package)
        
        if critique.passed:
            logger.info(f"Draft passed review for {bill_number}")
            return draft_analysis
        
        # 4. Refinement Phase
        logger.info(f"Refining draft based on critique for {bill_number}")
        final_analysis = await self._refine_draft(draft_analysis, critique, bill_text)
        
        return final_analysis

    async def _generate_draft(
        self, 
        bill_text: str, 
        bill_number: str, 
        jurisdiction: str,
        research: ResearchPackage
    ) -> LegislationAnalysisResponse:
        """Generate initial draft using Grok."""
        system_prompt = """
        You are an expert policy analyst. Analyze the legislation for cost-of-living impacts.
        Use the provided RESEARCH DATA to support your analysis with real evidence.
        """
        
        user_message = f"""
        BILL: {bill_number} ({jurisdiction})
        
        RESEARCH SUMMARY:
        {research.summary}
        
        SOURCES:
        {[s.url for s in research.sources]}
        
        TEXT:
        {bill_text[:10000]}... (truncated)
        """
        
        return await self.gen_client.chat.completions.create(
            model=self.gen_model,
            response_model=LegislationAnalysisResponse,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )

    async def _review_draft(
        self,
        bill_text: str,
        analysis: LegislationAnalysisResponse,
        research: ResearchPackage
    ) -> ReviewCritique:
        """Review the draft using GLM."""
        system_prompt = """
        You are a strict auditor. Review the provided analysis against the bill text and research.
        Verify every claim. Check for hallucinations. Ensure all impacts are supported by evidence.
        """
        
        user_message = f"""
        ANALYSIS TO REVIEW:
        {analysis.model_dump_json()}
        
        RESEARCH DATA:
        {research.model_dump_json()}
        
        BILL TEXT:
        {bill_text[:5000]}...
        """
        
        return await self.review_client.chat.completions.create(
            model=self.review_model,
            response_model=ReviewCritique,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )

    async def _refine_draft(
        self,
        draft: LegislationAnalysisResponse,
        critique: ReviewCritique,
        bill_text: str
    ) -> LegislationAnalysisResponse:
        """Refine the draft based on critique."""
        system_prompt = """
        You are an expert policy analyst. Update your previous analysis based on the auditor's critique.
        Fix factual errors, add missing impacts, and correct citations.
        """
        
        user_message = f"""
        PREVIOUS DRAFT:
        {draft.model_dump_json()}
        
        CRITIQUE:
        {critique.model_dump_json()}
        
        Please provide the FINAL corrected analysis.
        """
        
        return await self.gen_client.chat.completions.create(
            model=self.gen_model,
            response_model=LegislationAnalysisResponse,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
