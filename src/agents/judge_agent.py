"""
Judge Agent - Evaluates content from all agents and selects the best one for each location.

The Judge makes decisions based on:
1. Content quality and relevance to location
2. User profile (age, gender, preferences)
3. Number of available options (1, 2, or 3 agents responded)

Decision Logic:
- 3 agents → Compare all 3 against user profile, pick best
- 2 agents → Compare 2 against user profile, pick best
- 1 agent → Simple decision, use the available content

The Judge WAITS for the Smart Queue to provide results (with timeout mechanism).
"""
from typing import List, Optional, Dict, Any
import re

from src.agents.base_agent import BaseAgent
from src.models.content import ContentResult, ContentType
from src.models.route import RoutePoint
from src.models.decision import JudgeDecision
from src.models.user_profile import UserProfile, AgeGroup, Gender
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Agent skills (can be loaded from YAML)
AGENT_SKILLS = {}


class JudgeAgent(BaseAgent):
    """
    Agent specialized in evaluating and selecting the best content.
    
    Considers:
    - Location relevance
    - User demographics (kid/adult/senior, male/female)
    - User preferences (educational/entertainment/historical)
    - Content type appropriateness
    """
    
    def __init__(self, user_profile: Optional[UserProfile] = None):
        super().__init__("judge")
        self.evaluation_criteria = AGENT_SKILLS["judge_agent"]["scoring_criteria"]
        self.user_profile = user_profile or UserProfile()
    
    def get_content_type(self) -> ContentType:
        """Judge doesn't produce content, but returns the selected type."""
        return ContentType.TEXT  # Default, but actual type comes from selection
    
    def _search_content(self, point: RoutePoint) -> Optional[ContentResult]:
        """
        Judge doesn't search for content - use evaluate() instead.
        This is just to satisfy the abstract method.
        """
        return None
    
    def evaluate(
        self, 
        point: RoutePoint, 
        candidates: List[ContentResult],
        user_profile: Optional[UserProfile] = None
    ) -> JudgeDecision:
        """
        Evaluate all candidate content and select the best one.
        
        Decision logic based on number of candidates:
        - 3 candidates: Full comparison with user profile matching
        - 2 candidates: Compare both against user profile
        - 1 candidate: Simple decision (use what's available)
        
        Args:
            point: The route point being evaluated
            candidates: List of content results from other agents (1-3)
            user_profile: Optional user profile to override instance profile
            
        Returns:
            JudgeDecision with the selected content and reasoning
        """
        if not candidates:
            raise ValueError("No candidates to evaluate")
        
        # Use provided profile or fall back to instance profile
        profile = user_profile or self.user_profile
        
        num_candidates = len(candidates)
        logger.info(
            f"[Judge] Evaluating {num_candidates} candidate(s) for {point.location_name or point.address} "
            f"(User: {profile.age_group.value}, {profile.gender.value})"
        )
        
        # ═══════════════════════════════════════════════════════════════════
        # CASE 1: Only one candidate → Simple decision
        # ═══════════════════════════════════════════════════════════════════
        if num_candidates == 1:
            candidate = candidates[0]
            reasoning = self._generate_single_candidate_reasoning(candidate, profile)
            
            logger.info(f"[Judge] Single option available: {candidate.content_type.value}")
            
            return JudgeDecision(
                point_id=point.id,
                selected_content=candidate,
                all_candidates=candidates,
                reasoning=reasoning,
                scores={candidate.content_type: candidate.relevance_score}
            )
        
        # ═══════════════════════════════════════════════════════════════════
        # CASE 2: Two candidates → Compare against user profile
        # ═══════════════════════════════════════════════════════════════════
        if num_candidates == 2:
            evaluation = self._evaluate_two_candidates(point, candidates, profile)
        
        # ═══════════════════════════════════════════════════════════════════
        # CASE 3: Three candidates → Full comparison with profile
        # ═══════════════════════════════════════════════════════════════════
        else:
            evaluation = self._evaluate_candidates(point, candidates, profile)
        
        # Get the winner
        winner_idx = evaluation.get('winner_index', 0)
        if 0 <= winner_idx < len(candidates):
            winner = candidates[winner_idx]
        else:
            winner = candidates[0]
        
        # Update winner's relevance score with judge's score
        if evaluation.get('winner_score'):
            winner.relevance_score = evaluation['winner_score']
        
        decision = JudgeDecision(
            point_id=point.id,
            selected_content=winner,
            all_candidates=candidates,
            reasoning=evaluation.get('reasoning', 'Selected based on relevance'),
            scores=evaluation.get('scores', {c.content_type: c.relevance_score for c in candidates})
        )
        
        # Log the decision
        log_judge_decision(
            point.id,
            f"{winner.content_type.value}: {winner.title}",
            decision.reasoning
        )
        
        return decision
    
    def _generate_single_candidate_reasoning(
        self, 
        candidate: ContentResult, 
        profile: UserProfile
    ) -> str:
        """Generate reasoning when only one option is available."""
        content_type = candidate.content_type.value
        
        # Check if content type matches user preferences
        preferences = profile.get_content_type_preferences()
        type_key = content_type.lower()
        preference_score = preferences.get(type_key, 1.0)
        
        if preference_score > 1.2:
            match_quality = "excellent match"
        elif preference_score > 1.0:
            match_quality = "good match"
        elif preference_score < 0.8:
            match_quality = "acceptable (not ideal for user profile)"
        else:
            match_quality = "acceptable"
        
        return f"Only {content_type} content available - {match_quality} for {profile.age_group.value} user"
    
    def _evaluate_two_candidates(
        self,
        point: RoutePoint,
        candidates: List[ContentResult],
        profile: UserProfile
    ) -> Dict[str, Any]:
        """
        Evaluate two candidates (when one agent didn't respond).
        Uses user profile to make the decision.
        """
        location = point.location_name or point.address
        
        # Get user profile preferences
        type_preferences = profile.get_content_type_preferences()
        profile_context = profile.to_agent_context()
        profile_criteria = profile.to_judge_criteria()
        
        # Build candidate descriptions
        candidate_descriptions = []
        for i, c in enumerate(candidates):
            type_emoji = {
                ContentType.VIDEO: "🎬",
                ContentType.MUSIC: "🎵",
                ContentType.TEXT: "📖"
            }.get(c.content_type, "📄")
            
            candidate_descriptions.append(
                f"{i+1}. {type_emoji} [{c.content_type.value.upper()}] {c.title}\n"
                f"   Description: {c.description[:150] if c.description else 'N/A'}...\n"
                f"   Initial Score: {c.relevance_score:.1f}/10"
            )
        
        candidates_text = "\n\n".join(candidate_descriptions)
        
        prompt = f"""You are a tour guide content curator selecting content for a specific user.

**Location:** {location}

**User Profile:**
{profile_context}

**User Criteria:**
{profile_criteria}

**Available Content (2 options - one agent didn't respond in time):**

{candidates_text}

**Your Task:**
Compare these 2 content options and select the BEST one for this specific user at this location.

Consider:
1. Which content type (video/music/text) suits this user's age group and preferences?
2. Is the content appropriate for the user profile?
3. Does it enhance the travel experience for THIS specific user?

**Response Format:**
SCORES:
- Option 1: [score 0-10]
- Option 2: [score 0-10]

WINNER: [1 or 2]
WINNER_SCORE: [final score 0-10]
REASONING: [2-3 sentences explaining why this content is best for THIS user]"""

        try:
            response = self._call_llm(prompt)
            return self._parse_two_candidate_response(response, candidates)
        except Exception as e:
            logger.warning(f"Two-candidate evaluation failed: {e}")
            # Fallback: use profile preferences
            return self._fallback_two_candidate_selection(candidates, type_preferences)
    
    def _parse_two_candidate_response(
        self,
        response: str,
        candidates: List[ContentResult]
    ) -> Dict[str, Any]:
        """Parse LLM response for two-candidate evaluation."""
        result = {
            'scores': {},
            'winner_index': 0,
            'winner_score': 5.0,
            'reasoning': ''
        }
        
        try:
            # Parse winner
            winner_match = re.search(r'WINNER:\s*(\d+)', response)
            if winner_match:
                result['winner_index'] = int(winner_match.group(1)) - 1
            
            # Parse winner score
            winner_score_match = re.search(r'WINNER_SCORE:\s*([\d.]+)', response)
            if winner_score_match:
                result['winner_score'] = float(winner_score_match.group(1))
            
            # Parse reasoning
            reasoning_match = re.search(r'REASONING:\s*(.+?)(?=$|\n\n)', response, re.DOTALL)
            if reasoning_match:
                result['reasoning'] = reasoning_match.group(1).strip()
            
            # Set scores
            for i, c in enumerate(candidates):
                result['scores'][c.content_type] = c.relevance_score
            
        except Exception as e:
            logger.warning(f"Error parsing two-candidate response: {e}")
        
        return result
    
    def _fallback_two_candidate_selection(
        self,
        candidates: List[ContentResult],
        type_preferences: Dict[str, float]
    ) -> Dict[str, Any]:
        """Fallback selection based on user profile preferences."""
        scored = []
        for i, c in enumerate(candidates):
            type_key = c.content_type.value.lower()
            preference_multiplier = type_preferences.get(type_key, 1.0)
            adjusted_score = c.relevance_score * preference_multiplier
            scored.append((i, c, adjusted_score))
        
        # Sort by adjusted score
        scored.sort(key=lambda x: x[2], reverse=True)
        best_idx, best_content, best_score = scored[0]
        
        return {
            'winner_index': best_idx,
            'winner_score': min(best_score, 10.0),
            'reasoning': f"Selected {best_content.content_type.value} based on user profile preferences",
            'scores': {c.content_type: c.relevance_score for c in candidates}
        }
    
    def _evaluate_candidates(
        self, 
        point: RoutePoint, 
        candidates: List[ContentResult],
        profile: UserProfile
    ) -> Dict[str, Any]:
        """
        Use LLM to evaluate and rank all 3 candidates with user profile.
        
        Args:
            point: The route point
            candidates: List of content candidates (typically 3)
            profile: User profile for personalization
            
        Returns:
            Evaluation results dictionary
        """
        location = point.location_name or point.address
        
        # Get user profile context
        profile_context = profile.to_agent_context()
        profile_criteria = profile.to_judge_criteria()
        
        # Build candidate descriptions
        candidate_descriptions = []
        for i, c in enumerate(candidates):
            type_emoji = {
                ContentType.VIDEO: "🎬",
                ContentType.MUSIC: "🎵",
                ContentType.TEXT: "📖"
            }.get(c.content_type, "📄")
            
            candidate_descriptions.append(
                f"{i+1}. {type_emoji} [{c.content_type.value.upper()}] {c.title}\n"
                f"   Source: {c.source}\n"
                f"   Description: {c.description[:150] if c.description else 'N/A'}...\n"
                f"   Initial Score: {c.relevance_score:.1f}/10"
            )
        
        candidates_text = "\n\n".join(candidate_descriptions)
        
        # Build evaluation criteria text (system + user-specific)
        system_criteria = "\n".join(f"- {c}" for c in self.evaluation_criteria)
        
        prompt = f"""You are an expert tour guide content curator selecting the BEST content for a SPECIFIC user.

**Location:** {location}
**Full Address:** {point.address}

═══════════════════════════════════════════════════════════════════
USER PROFILE (CRITICAL - Match content to this user!)
═══════════════════════════════════════════════════════════════════
{profile_context}

**User-Specific Criteria:**
{profile_criteria}

═══════════════════════════════════════════════════════════════════
AVAILABLE CONTENT (All 3 agents responded)
═══════════════════════════════════════════════════════════════════

{candidates_text}

═══════════════════════════════════════════════════════════════════
EVALUATION
═══════════════════════════════════════════════════════════════════

**System Criteria:**
{system_criteria}

**Your Task:**
1. Score each content option (0-10) considering BOTH location relevance AND user profile match
2. Select the BEST single piece of content for THIS SPECIFIC USER at this location
3. Explain your decision with reference to the user profile

Consider:
- Is a {profile.age_group.value} user more likely to enjoy video, music, or text?
- Does the content match the user's stated preferences?
- Is the content appropriate for the user's demographics?
- Which content type creates the best experience for THIS user?

**Response Format:**
SCORES:
- Video: [score 0-10]
- Music: [score 0-10]  
- Text: [score 0-10]

WINNER: [number 1-{len(candidates)}]
WINNER_SCORE: [final score 0-10]
REASONING: [2-3 sentences explaining why this content is the best choice for THIS USER at this location]"""

        try:
            response = self._call_llm(prompt)
            return self._parse_evaluation_response(response, candidates)
        except Exception as e:
            logger.warning(f"Evaluation failed: {e}")
            # Fallback: use profile preferences
            type_preferences = profile.get_content_type_preferences()
            scored = []
            for i, c in enumerate(candidates):
                type_key = c.content_type.value.lower()
                multiplier = type_preferences.get(type_key, 1.0)
                adjusted_score = c.relevance_score * multiplier
                scored.append((i, adjusted_score))
            
            best_idx = max(scored, key=lambda x: x[1])[0]
            return {
                'winner_index': best_idx,
                'winner_score': candidates[best_idx].relevance_score,
                'reasoning': f'Selected based on user profile preferences ({profile.age_group.value})',
                'scores': {c.content_type: c.relevance_score for c in candidates}
            }
    
    def _parse_evaluation_response(
        self, 
        response: str, 
        candidates: List[ContentResult]
    ) -> Dict[str, Any]:
        """Parse the LLM evaluation response."""
        
        result = {
            'scores': {},
            'winner_index': 0,
            'winner_score': 5.0,
            'reasoning': ''
        }
        
        try:
            # Parse scores
            video_match = re.search(r'Video:\s*([\d.]+)', response, re.IGNORECASE)
            music_match = re.search(r'Music:\s*([\d.]+)', response, re.IGNORECASE)
            text_match = re.search(r'Text:\s*([\d.]+)', response, re.IGNORECASE)
            
            if video_match:
                result['scores'][ContentType.VIDEO] = float(video_match.group(1))
            if music_match:
                result['scores'][ContentType.MUSIC] = float(music_match.group(1))
            if text_match:
                result['scores'][ContentType.TEXT] = float(text_match.group(1))
            
            # Parse winner
            winner_match = re.search(r'WINNER:\s*(\d+)', response)
            if winner_match:
                result['winner_index'] = int(winner_match.group(1)) - 1
            
            # Parse winner score
            winner_score_match = re.search(r'WINNER_SCORE:\s*([\d.]+)', response)
            if winner_score_match:
                result['winner_score'] = float(winner_score_match.group(1))
            
            # Parse reasoning
            reasoning_match = re.search(r'REASONING:\s*(.+?)(?=$|\n\n)', response, re.DOTALL)
            if reasoning_match:
                result['reasoning'] = reasoning_match.group(1).strip()
            else:
                # Try to get any text after REASONING
                parts = response.split('REASONING:')
                if len(parts) > 1:
                    result['reasoning'] = parts[1].strip()[:200]
            
            # Validate winner index
            if result['winner_index'] < 0 or result['winner_index'] >= len(candidates):
                result['winner_index'] = 0
                
        except Exception as e:
            logger.warning(f"Error parsing evaluation: {e}")
        
        return result
    
    def quick_evaluate(
        self, 
        point: RoutePoint, 
        candidates: List[ContentResult],
        user_profile: Optional[UserProfile] = None
    ) -> ContentResult:
        """
        Quick evaluation without full LLM analysis.
        Uses simple scoring heuristics + user profile preferences.
        
        Args:
            point: The route point
            candidates: List of content candidates
            user_profile: Optional user profile
            
        Returns:
            Best content result
        """
        if not candidates:
            raise ValueError("No candidates to evaluate")
        
        if len(candidates) == 1:
            return candidates[0]
        
        profile = user_profile or self.user_profile
        location = (point.location_name or point.address).lower()
        type_preferences = profile.get_content_type_preferences()
        
        # Score each candidate
        scored_candidates = []
        for c in candidates:
            score = c.relevance_score
            
            # Apply user profile preference multiplier
            type_key = c.content_type.value.lower()
            profile_multiplier = type_preferences.get(type_key, 1.0)
            score *= profile_multiplier
            
            # Boost for location mention in title
            if location in c.title.lower():
                score += 2.0
            
            # Boost for historical content at historical sites
            if c.metadata.get('is_historical') or c.metadata.get('fact_type') == 'historical':
                if any(word in location for word in ['museum', 'memorial', 'ancient', 'old']):
                    score += 1.5
            
            # Slight preference for video at scenic locations
            if c.content_type == ContentType.VIDEO:
                if any(word in location for word in ['view', 'park', 'beach', 'mountain']):
                    score += 1.0
            
            # Slight preference for music at cultural locations
            if c.content_type == ContentType.MUSIC:
                if any(word in location for word in ['theatre', 'concert', 'festival']):
                    score += 1.0
            
            # Age-specific boosts
            if profile.age_group == AgeGroup.KID:
                # Kids love animated/fun content
                if 'fun' in c.title.lower() or 'kids' in c.title.lower():
                    score += 1.5
            elif profile.age_group == AgeGroup.SENIOR:
                # Seniors appreciate classic/historical content
                if 'classic' in c.title.lower() or 'history' in c.title.lower():
                    score += 1.5
            
            scored_candidates.append((c, min(score, 10.0)))
        
        # Return highest scored
        best = max(scored_candidates, key=lambda x: x[1])
        best[0].relevance_score = best[1]
        
        return best[0]

