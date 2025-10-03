import random
from typing import Dict, List, Any

class AgriculturalKnowledgeBase:
    def __init__(self):
        self.diseases = self.load_disease_database()
        self.fertilizers = self.load_fertilizer_guide()
        self.planting_procedures = self.load_planting_procedures()
        self.crop_care_calendar = self.load_crop_care_calendar()
        self.pests = self.load_pest_database()
        self.yield_maximization = self.load_yield_tips()
        self.conversational_templates = self.load_conversational_templates()
    
    def load_disease_database(self):
        """Comprehensive disease database for all crops"""
        return {
            'maize': {
                'maize_streak_virus': {
                    'symptoms': ['Yellow streaks on leaves', 'Stunted growth', 'Reduced yield', 'Leaf distortion'],
                    'causes': ['Leafhopper insects', 'Infected seeds', 'Poor field sanitation'],
                    'treatment': ['Use resistant varieties', 'Control leafhoppers with neem oil', 'Remove infected plants', 'Apply systemic insecticide'],
                    'prevention': ['Plant certified seeds', 'Crop rotation', 'Early planting', 'Control vector insects']
                },
                'maize_blight': {
                    'symptoms': ['Brown spots on leaves', 'Leaf death', 'Poor ear development', 'Gray mold on ears'],
                    'causes': ['Fungal infection', 'High humidity', 'Poor air circulation', 'Wet conditions'],
                    'treatment': ['Apply copper-based fungicide', 'Remove affected leaves', 'Improve drainage', 'Reduce plant density'],
                    'prevention': ['Plant resistant varieties', 'Proper spacing', 'Avoid overhead watering', 'Crop rotation']
                },
                'armyworm': {
                    'symptoms': ['Holes in leaves', 'Cut stems', 'Missing plant parts', 'Visible caterpillars'],
                    'causes': ['Fall armyworm moths', 'Poor field monitoring', 'Dense planting'],
                    'treatment': ['Hand picking', 'Bt spray', 'Neem oil', 'Chemical pesticides as last resort'],
                    'prevention': ['Early detection', 'Trap crops', 'Natural predators', 'Crop rotation']
                }
            },
            'pepper': {
                'pepper_blight': {
                    'symptoms': ['Dark spots on leaves and fruits', 'Fruit rot', 'Leaf yellowing', 'Plant wilting'],
                    'causes': ['Fungal infection', 'Excessive moisture', 'Poor ventilation', 'Contaminated tools'],
                    'treatment': ['Remove infected parts', 'Apply fungicide', 'Improve air circulation', 'Reduce watering'],
                    'prevention': ['Proper spacing', 'Avoid overhead watering', 'Use clean tools', 'Crop rotation']
                },
                'bacterial_wilt': {
                    'symptoms': ['Sudden wilting', 'Brown vascular tissue', 'Plant death', 'No recovery after watering'],
                    'causes': ['Bacterial infection', 'Soil contamination', 'Root damage', 'Poor drainage'],
                    'treatment': ['Remove infected plants', 'Soil treatment', 'Improve drainage', 'Use resistant varieties'],
                    'prevention': ['Soil sterilization', 'Certified seeds', 'Proper drainage', 'Crop rotation']
                }
            },
            'tomatoes': {
                'tomato_blight': {
                    'symptoms': ['Brown spots on leaves and fruits', 'Leaf yellowing', 'Fruit rot', 'White mold'],
                    'causes': ['Fungal infection', 'High humidity', 'Poor air circulation', 'Contaminated water'],
                    'treatment': ['Apply fungicide', 'Remove infected parts', 'Improve ventilation', 'Reduce humidity'],
                    'prevention': ['Proper spacing', 'Avoid wet foliage', 'Use resistant varieties', 'Crop rotation']
                },
                'whitefly_damage': {
                    'symptoms': ['Yellow sticky leaves', 'Stunted growth', 'Sooty mold', 'Virus transmission'],
                    'causes': ['Whitefly infestation', 'Poor monitoring', 'Nearby weeds', 'Favorable conditions'],
                    'treatment': ['Yellow sticky traps', 'Neem oil spray', 'Beneficial insects', 'Systemic insecticides'],
                    'prevention': ['Regular monitoring', 'Weed control', 'Reflective mulch', 'Companion planting']
                },
                'blight': {
                    'symptoms': ['Brown spots on leaves and fruits', 'Wilting', 'Fruit rot'],
                    'causes': ['Fungal infection', 'Wet conditions', 'Poor ventilation'],
                    'treatment': ['Apply fungicide', 'Remove infected parts', 'Improve air circulation'],
                    'prevention': ['Use resistant varieties', 'Proper spacing', 'Avoid wet foliage']
                }
            },
            'cassava': {
                'cassava_mosaic_disease': {
                    'symptoms': ['Yellow and green mosaic on leaves', 'Leaf distortion', 'Reduced root size', 'Stunted growth'],
                    'causes': ['Whitefly transmission', 'Infected cuttings', 'Poor sanitation', 'Viral infection'],
                    'treatment': ['Remove infected plants', 'Control whiteflies', 'Use healthy cuttings', 'Field sanitation'],
                    'prevention': ['Use certified material', 'Control vector insects', 'Crop rotation', 'Regular monitoring']
                }
            },
            'beans': {
                'bean_rust': {
                    'symptoms': ['Orange pustules on leaves', 'Leaf yellowing', 'Premature leaf drop', 'Reduced yield'],
                    'causes': ['Fungal spores', 'High humidity', 'Cool temperatures', 'Poor air circulation'],
                    'treatment': ['Fungicide application', 'Remove infected leaves', 'Improve spacing', 'Reduce humidity'],
                    'prevention': ['Resistant varieties', 'Proper spacing', 'Avoid overhead irrigation', 'Crop rotation']
                }
            }
        }
    
    def load_fertilizer_guide(self):
        """Comprehensive fertilizer recommendations"""
        return {
            'maize': {
                'basal_fertilizer': {
                    'npk': '20-10-10',
                    'rate': '300kg per hectare',
                    'timing': 'At planting',
                    'application': 'Mix with soil in planting holes or broadcast before planting'
                },
                'top_dressing': {
                    'fertilizer': 'Urea (46-0-0)',
                    'rate': '150kg per hectare',
                    'timing': '4-6 weeks after planting',
                    'application': 'Side dress around plants, 5cm from stem, then water'
                },
                'organic_options': {
                    'compost': '2-3 tons per hectare before planting',
                    'chicken_manure': '1 ton per hectare, well decomposed',
                    'cow_manure': '3-4 tons per hectare',
                    'green_manure': 'Legume cover crops before main season'
                }
            },
            'pepper': {
                'nursery_stage': {
                    'fertilizer': 'NPK 15-15-15',
                    'rate': '50g per square meter of nursery bed',
                    'timing': 'Before sowing seeds',
                    'application': 'Mix thoroughly with nursery soil'
                },
                'transplanting': {
                    'fertilizer': 'Compost + NPK 20-10-20',
                    'rate': '200kg NPK + 2 tons compost per hectare',
                    'timing': 'At transplanting',
                    'application': 'Apply in planting holes'
                },
                'maintenance': {
                    'fertilizer': 'NPK 15-15-15',
                    'rate': '100kg per hectare every 3 weeks',
                    'timing': 'Throughout growing season',
                    'application': 'Side dress and water immediately'
                }
            },
            'tomatoes': {
                'nursery_fertilizer': {
                    'fertilizer': 'Compost + bone meal',
                    'rate': '1:1 ratio with soil',
                    'timing': 'Before sowing',
                    'application': 'Mix thoroughly with nursery medium'
                },
                'transplant_fertilizer': {
                    'fertilizer': 'NPK 20-10-20',
                    'rate': '250kg per hectare',
                    'timing': 'At transplanting',
                    'application': 'Apply in planting holes and cover with soil'
                },
                'fruiting_stage': {
                    'fertilizer': 'High potassium fertilizer',
                    'rate': '150kg per hectare bi-weekly',
                    'timing': 'When first fruits form',
                    'application': 'Side dress and water thoroughly'
                }
            },
            'cassava': {
                'minimal_fertilizer': {
                    'note': 'Cassava grows well in poor soils but responds to fertilizer',
                    'npk': '15-15-15',
                    'rate': '200kg per hectare',
                    'timing': '2 months after planting',
                    'application': 'Band application around plants'
                },
                'organic_approach': {
                    'compost': '1-2 tons per hectare',
                    'wood_ash': '100kg per hectare for potassium',
                    'timing': 'Before planting and at 3 months',
                    'application': 'Broadcast and incorporate into soil'
                }
            },
            'beans': {
                'phosphorus_focus': {
                    'fertilizer': 'DAP (18-46-0)',
                    'rate': '100kg per hectare',
                    'timing': 'At planting',
                    'application': 'Band application 5cm from seeds'
                },
                'maintenance': {
                    'fertilizer': 'Potassium sulfate',
                    'rate': '50kg per hectare',
                    'timing': 'At flowering',
                    'application': 'Side dress and water'
                }
            },
            'vegetables': {
                'general': {
                    'npk': '20-10-20',
                    'rate': '400-500kg per hectare',
                    'timing': 'Split applications every 2-3 weeks',
                    'organic': 'Compost 3-4 tons per hectare + liquid fertilizer weekly'
                }
            }
        }
    
    def load_planting_procedures(self):
        """Comprehensive planting procedures for all crops"""
        return {
            'maize': {
                'land_preparation': [
                    'Clear land of weeds, debris, and previous crop residues',
                    'Plow or till soil to 20-25cm depth when soil moisture is optimal',
                    'Make ridges or beds if area has drainage issues',
                    'Test soil pH (ideal range: 6.0-7.0) and adjust if necessary',
                    'Incorporate organic matter like compost or well-rotted manure'
                ],
                'seed_preparation': [
                    'Purchase certified seeds from approved dealers or cooperatives',
                    'Check seed germination rate (should be above 85%)',
                    'Treat seeds with appropriate fungicide to prevent soil-borne diseases',
                    'Store seeds in cool, dry place until planting'
                ],
                'planting': [
                    'Plant at beginning of rainy season (March-May in most regions)',
                    'Make planting holes 75cm between rows and 25cm within rows',
                    'Plant 2-3 seeds per hole at depth of 3-5cm',
                    'Cover seeds lightly with soil and press gently',
                    'Apply basal fertilizer in planting holes before covering'
                ],
                'post_planting': [
                    'Water if rainfall is inadequate (seeds need moisture to germinate)',
                    'Thin to 1-2 strongest plants per stand 2 weeks after emergence',
                    'Begin weeding program - keep field weed-free for first 6 weeks',
                    'Apply top-dressing fertilizer 4-6 weeks after planting',
                    'Monitor for pests and diseases throughout growing season'
                ]
            },
            'pepper': {
                'land_preparation': [
                    'Choose well-drained location with 6+ hours daily sunlight',
                    'Clear and plow land thoroughly to break up compacted soil',
                    'Make raised beds 1-1.2m wide and 20-30cm high for drainage',
                    'Incorporate 3-4 tons of well-composted organic matter per hectare',
                    'Ensure soil pH is between 6.0-6.8 for optimal nutrient uptake'
                ],
                'nursery_management': [
                    'Prepare nursery beds with fine, well-drained soil mixture',
                    'Mix equal parts garden soil, compost, and sand',
                    'Soak pepper seeds in warm water for 6-8 hours before sowing',
                    'Sow seeds 1cm deep in nursery beds with 2cm spacing',
                    'Cover nursery with shade cloth and water gently twice daily'
                ],
                'transplanting': [
                    'Transplant seedlings when they have 4-6 true leaves (4-6 weeks)',
                    'Space plants 30-40cm apart in rows 60-75cm apart',
                    'Transplant in evening or on cloudy days to reduce shock',
                    'Water immediately after transplanting and daily for first week',
                    'Provide temporary shade for 3-5 days after transplanting'
                ],
                'post_planting': [
                    'Install stakes or cages when plants reach 15-20cm height',
                    'Apply organic mulch around plants to retain moisture',
                    'Water regularly but avoid waterlogging - peppers need consistent moisture',
                    'Side-dress with compost or balanced fertilizer every 3-4 weeks',
                    'Monitor for pests like aphids, whiteflies, and spider mites'
                ]
            },
            'tomatoes': {
                'nursery_preparation': [
                    'Prepare seedbed with mixture of garden soil, compost, and sand (2:1:1)',
                    'Sterilize soil mixture by solar heating or steam treatment',
                    'Sow tomato seeds 0.5-1cm deep in rows 10cm apart',
                    'Maintain soil temperature at 20-25°C for optimal germination',
                    'Water gently with fine spray to avoid disturbing seeds'
                ],
                'seedling_care': [
                    'Provide 12-14 hours of light daily (natural or artificial)',
                    'Maintain consistent moisture but avoid waterlogging',
                    'Begin hardening process 1 week before transplanting',
                    'Gradually expose seedlings to outdoor conditions',
                    'Ensure seedlings are 15-20cm tall with 5-7 leaves before transplanting'
                ],
                'transplanting': [
                    'Prepare main field with raised beds 1m wide, 20cm high',
                    'Space plants 45-60cm apart in rows 1-1.2m apart',
                    'Dig planting holes slightly larger than root ball',
                    'Plant seedlings deeper than they were in nursery (up to first leaves)',
                    'Water thoroughly immediately after transplanting'
                ],
                'support_and_maintenance': [
                    'Install stakes (1.5-2m tall) or cages within 2 weeks of transplanting',
                    'Tie plants to supports using soft materials, check weekly',
                    'Remove suckers (shoots between main stem and branches) regularly',
                    'Apply balanced fertilizer every 2-3 weeks throughout season',
                    'Monitor for common pests and diseases, treat promptly'
                ]
            },
            'cassava': {
                'land_preparation': [
                    'Clear field of weeds and previous crop residues',
                    'Plow or till soil to loosen compacted areas',
                    'Make ridges 1m apart and 15-20cm high in areas with poor drainage',
                    'Cassava tolerates poor soils but benefits from organic matter addition'
                ],
                'stem_cutting_preparation': [
                    'Select healthy, mature stems from 8-12 month old plants',
                    'Cut stems into pieces 15-20cm long with 5-7 nodes',
                    'Use sharp, clean knife to avoid damaging cuttings',
                    'Plant cuttings within 24 hours of cutting for best results'
                ],
                'planting': [
                    'Plant at beginning of rainy season for rain-fed cultivation',
                    'Place cuttings at 45-degree angle in planting holes',
                    'Bury 2/3 of cutting length, leaving 1/3 above ground',
                    'Space plants 1m x 1m (10,000 plants per hectare)',
                    'Water lightly if rains are delayed'
                ],
                'post_planting': [
                    'Weed regularly for first 3-4 months when plants establish',
                    'Hill soil around plants at 3 and 6 months to promote root development',
                    'Monitor for cassava mosaic disease and remove infected plants',
                    'Harvest can begin at 8-12 months depending on variety and use'
                ]
            },
            'beans': {
                'land_preparation': [
                    'Select well-drained soil with good organic matter content',
                    'Plow field when soil moisture is at field capacity',
                    'Make ridges 30cm apart for bush beans, 60cm for climbing varieties',
                    'Incorporate compost or aged manure 2-3 weeks before planting'
                ],
                'seed_preparation': [
                    'Use certified seeds with high germination rate (>90%)',
                    'Sort seeds, remove damaged or diseased ones',
                    'Inoculate with rhizobia bacteria for improved nitrogen fixation',
                    'Treat seeds with fungicide if soil-borne diseases are a concern'
                ],
                'planting': [
                    'Plant at onset of rainy season or with assured water supply',
                    'Sow seeds 3-4cm deep and 10-15cm apart within rows',
                    'Plant 2-3 seeds per hole and thin to strongest plant',
                    'Ensure soil temperature is above 15°C for good germination',
                    'Water gently if rains are insufficient in first 2 weeks'
                ],
                'post_planting': [
                    'Provide support structures for climbing varieties',
                    'Begin weeding 2-3 weeks after emergence',
                    'Apply phosphorus-rich fertilizer at flowering stage',
                    'Monitor for pests like bean fly, aphids, and pod borers',
                    'Harvest pods when they are full but still tender for fresh consumption'
                ]
            }
        }
    
    def load_crop_care_calendar(self):
        """Monthly care calendar for crops"""
        return {
            'maize': {
                'month_1': ['Plant seeds', 'Apply basal fertilizer', 'Weed around plants'],
                'month_2': ['Apply top-dressing fertilizer', 'Continue weeding', 'Check for pests'],
                'month_3': ['Monitor for diseases', 'Support tall plants', 'Reduce watering'],
                'month_4': ['Harvest when kernels are hard', 'Dry properly', 'Store safely']
            },
            'cassava': {
                'month_1': ['Plant stem cuttings', 'Weed regularly'],
                'month_2-3': ['Continue weeding', 'Check for diseases'],
                'month_4-6': ['Reduce weeding', 'Monitor growth'],
                'month_8-12': ['Harvest mature roots', 'Process quickly']
            },
            'tomatoes': {
                'month_1': ['Start nursery', 'Prepare transplant beds'],
                'month_2': ['Transplant seedlings', 'Install support structures'],
                'month_3-4': ['Regular fertilization', 'Pest and disease monitoring'],
                'month_4-6': ['Harvest ripe fruits', 'Continue care for continuous production']
            },
            'pepper': {
                'month_1': ['Prepare nursery', 'Sow seeds'],
                'month_2': ['Transplant to field', 'Apply mulch'],
                'month_3-6': ['Regular harvesting', 'Continuous fertilization'],
                'month_6+': ['End-of-season cleanup', 'Prepare for next crop']
            },
            'beans': {
                'month_1': ['Plant seeds', 'Initial weeding'],
                'month_2': ['Apply fertilizer at flowering', 'Continue pest monitoring'],
                'month_3': ['Harvest pods regularly', 'Water as needed'],
                'month_4': ['Final harvest', 'Prepare land for next crop']
            }
        }
    
    def load_pest_database(self):
        """Common pests and their control"""
        return {
            'maize': {
                'fall_armyworm': {
                    'identification': 'Small caterpillars eating leaves, active at night',
                    'damage': 'Holes in leaves, stunted growth, reduced yield',
                    'control': ['Handpicking', 'Neem oil spray', 'Bt spray', 'Pheromone traps'],
                    'prevention': ['Early planting', 'Trap crops', 'Natural predators', 'Field sanitation']
                },
                'stem_borer': {
                    'identification': 'Caterpillars boring into stems',
                    'damage': 'Holes in stems, broken stems, reduced yield',
                    'control': ['Remove and destroy affected plants', 'Biological control agents'],
                    'prevention': ['Clean cultivation', 'Resistant varieties', 'Proper timing']
                }
            },
            'tomatoes': {
                'whiteflies': {
                    'identification': 'Tiny white flying insects under leaves',
                    'damage': 'Yellow leaves, virus transmission, reduced vigor',
                    'control': ['Yellow sticky traps', 'Neem oil', 'Reflective mulch', 'Beneficial insects'],
                    'prevention': ['Remove weeds', 'Companion planting', 'Screen houses', 'Regular monitoring']
                },
                'aphids': {
                    'identification': 'Small green or black insects on young shoots',
                    'damage': 'Curled leaves, stunted growth, virus transmission',
                    'control': ['Soap spray', 'Neem oil', 'Ladybirds', 'Water spray'],
                    'prevention': ['Reflective mulch', 'Companion planting', 'Avoid over-fertilization']
                }
            },
            'pepper': {
                'thrips': {
                    'identification': 'Tiny insects causing silver streaks on leaves',
                    'damage': 'Leaf damage, reduced photosynthesis, virus transmission',
                    'control': ['Blue sticky traps', 'Beneficial mites', 'Neem oil'],
                    'prevention': ['Weed control', 'Resistant varieties', 'Proper spacing']
                }
            },
            'cassava': {
                'cassava_mealybug': {
                    'identification': 'White cottony insects on stems and leaves',
                    'damage': 'Stunted growth, yellowing, reduced root yield',
                    'control': ['Biological control agents', 'Soap spray', 'Systemic insecticides'],
                    'prevention': ['Use clean planting material', 'Field sanitation', 'Natural enemies']
                }
            },
            'beans': {
                'bean_fly': {
                    'identification': 'Small flies laying eggs in young stems',
                    'damage': 'Stem damage, wilting, plant death',
                    'control': ['Early planting', 'Resistant varieties', 'Soil treatment'],
                    'prevention': ['Seed treatment', 'Crop rotation', 'Field hygiene']
                }
            }
        }
    
    def load_yield_tips(self):
        """Tips for maximum yield"""
        return {
            'maize': [
                'Use certified high-yielding varieties adapted to local conditions',
                'Plant at optimal spacing (75cm x 25cm) for proper development',
                'Apply fertilizer in split doses - basal and top-dressing',
                'Maintain proper soil moisture throughout growing season',
                'Control weeds for first 6 weeks when competition is critical',
                'Harvest at correct maturity when moisture content is 20-25%',
                'Practice crop rotation to maintain soil fertility'
            ],
            'cassava': [
                'Use healthy stem cuttings from mature, disease-free plants',
                'Plant at start of rainy season for optimal establishment',
                'Maintain weed-free environment especially in first 3 months',
                'Hill soil around plants to promote root development',
                'Harvest at 8-10 months for best starch content',
                'Process tubers within 24 hours of harvest to prevent spoilage'
            ],
            'tomatoes': [
                'Choose varieties suited to local climate and market demands',
                'Provide adequate support structures for proper plant development',
                'Maintain consistent soil moisture with drip irrigation if possible',
                'Remove suckers regularly to focus energy on fruit production',
                'Apply balanced fertilization throughout growing season',
                'Harvest fruits at proper ripeness stage for intended use',
                'Practice integrated pest management for healthy plants'
            ],
            'pepper': [
                'Select appropriate varieties for local conditions and market',
                'Provide consistent moisture without waterlogging',
                'Use organic mulch to maintain soil temperature and moisture',
                'Apply balanced fertilization with emphasis on potassium during fruiting',
                'Harvest fruits regularly to encourage continuous production',
                'Provide adequate plant spacing for air circulation'
            ],
            'beans': [
                'Use certified seeds with high germination rate',
                'Inoculate seeds with rhizobia for better nitrogen fixation',
                'Plant at optimal density based on variety type',
                'Provide support for climbing varieties',
                'Apply phosphorus-rich fertilizer at flowering',
                'Harvest at proper maturity for intended use',
                'Practice crop rotation with non-legume crops'
            ],
            'vegetables': [
                'Use quality seeds or seedlings from reputable sources',
                'Provide adequate spacing based on crop requirements',
                'Water regularly but avoid waterlogging conditions',
                'Apply organic matter regularly to improve soil structure',
                'Practice crop rotation to prevent soil-borne diseases',
                'Harvest at proper maturity for maximum quality and yield'
            ]
        }
    
    def load_conversational_templates(self):
        """Templates for natural conversation responses"""
        return {
            'greetings': [
                "Hello {name}! I'm AgriBot, your farming assistant. I'm here to help with any agricultural questions you have. What's on your mind today?",
                "Hi there {name}! Great to meet you. I'm here to help with all your farming needs. What would you like to know?",
                "Welcome {name}! I'm excited to help you with your agricultural journey. What farming topic interests you today?",
                "Hello {name}! Ready to talk farming? I can help with crops, diseases, fertilizers, planting - you name it!"
            ],
            'thanks_responses': [
                "You're very welcome, {name}! I'm here to help whenever you need farming advice.",
                "Happy to help! Feel free to ask if you have more questions about your crops.",
                "No problem at all! I'm always here for your agricultural questions.",
                "You're welcome! Is there anything else about farming I can help you with?"
            ],
            'praise_responses': [
                "Thank you, {name}! I'm glad I could provide useful information. What else would you like to know?",
                "I appreciate that! I'm here to support your farming success. Any other questions?",
                "Thanks! It makes me happy when I can provide helpful farming advice. What's your next question?",
                "I'm glad you found that helpful! Feel free to ask about any other farming topics."
            ],
            'planting_intros': [
                "Let me guide you through growing {crop}!",
                "Growing {crop} is definitely doable - here's how:",
                "I'd be happy to help you with {crop} cultivation.",
                "{crop_title} is a great choice! Here's what you need to know:",
                "Perfect timing to learn about {crop}! Let me walk you through it."
            ],
            'disease_intros': [
                "That sounds concerning. Let me help you figure out what might be affecting your {crop}.",
                "I understand your worry about your {crop}. Let's identify the problem together.",
                "Plant health issues can be stressful. Let me help diagnose what's happening with your {crop}.",
                "Don't worry - many {crop} problems are treatable. Let's figure out what's going on."
            ]
        }
    
    def get_disease_info(self, crop, disease_name=None):
        """Get disease information for a crop"""
        crop_diseases = self.diseases.get(crop.lower(), {})
        
        if disease_name:
            disease_name = disease_name.lower().replace(' ', '_')
            disease_info = crop_diseases.get(disease_name)
            if disease_info:
                return {
                    'crop': crop,
                    'disease': disease_name,
                    'info': disease_info
                }
            else:
                return {'error': f'Disease "{disease_name}" not found for {crop}'}
        else:
            return {
                'crop': crop,
                'available_diseases': list(crop_diseases.keys()),
                'disease_count': len(crop_diseases)
            }
    
    def get_fertilizer_recommendation(self, crop, growth_stage='all'):
        """Get fertilizer recommendations"""
        crop_fertilizers = self.fertilizers.get(crop.lower(), {})
        
        if not crop_fertilizers:
            return {
                'crop': crop,
                'recommendation': 'General recommendation: Use balanced NPK 20-10-20 at 300kg/ha',
                'note': 'Specific data not available for this crop'
            }
        
        if growth_stage == 'all':
            return {
                'crop': crop,
                'fertilizer_program': crop_fertilizers
            }
        else:
            stage_info = crop_fertilizers.get(growth_stage)
            return {
                'crop': crop,
                'growth_stage': growth_stage,
                'recommendation': stage_info if stage_info else 'Stage not found'
            }
    
    def get_planting_guide(self, crop):
        """Get complete planting guide"""
        planting_info = self.planting_procedures.get(crop.lower())
        
        if planting_info:
            return {
                'crop': crop,
                'planting_guide': planting_info,
                'estimated_time': self.get_planting_timeline(crop)
            }
        else:
            return {
                'crop': crop,
                'error': 'Planting guide not available for this crop',
                'general_advice': [
                    'Prepare land by clearing and tilling',
                    'Use certified seeds',
                    'Plant at recommended spacing',
                    'Apply fertilizer as needed',
                    'Maintain proper weeding and watering'
                ]
            }
    
    def get_planting_timeline(self, crop):
        """Get timeline from planting to harvest"""
        timelines = {
            'maize': {
                'germination': '7-14 days',
                'tasseling': '60-70 days',
                'maturity': '90-120 days',
                'harvest': '110-130 days'
            },
            'cassava': {
                'sprouting': '14-21 days',
                'root_development': '3-4 months',
                'harvest': '8-12 months'
            },
            'tomatoes': {
                'germination': '7-10 days',
                'transplanting': '4-6 weeks',
                'flowering': '6-8 weeks after transplanting',
                'first_harvest': '10-12 weeks after transplanting'
            },
            'beans': {
                'germination': '5-7 days',
                'flowering': '35-45 days',
                'pod_filling': '50-60 days',
                'harvest': '70-90 days'
            },
            'pepper': {
                'germination': '10-14 days',
                'transplanting': '6-8 weeks',
                'flowering': '8-10 weeks after transplanting',
                'first_harvest': '12-14 weeks after transplanting'
            }
        }
        
        return timelines.get(crop.lower(), {
            'general': 'Timeline varies by crop variety and conditions'
        })
    
    def get_pest_info(self, crop, pest_name=None):
        """Get pest information"""
        crop_pests = self.pests.get(crop.lower(), {})
        
        if pest_name:
            pest_info = crop_pests.get(pest_name.lower().replace(' ', '_'))
            return {
                'crop': crop,
                'pest': pest_name,
                'info': pest_info if pest_info else 'Pest information not available'
            }
        else:
            return {
                'crop': crop,
                'available_pests': list(crop_pests.keys())
            }
    
    def get_yield_tips(self, crop):
        """Get yield maximization tips"""
        tips = self.yield_maximization.get(crop.lower())
        if tips:
            return {
                'crop': crop,
                'yield_tips': tips
            }
        else:
            return {
                'crop': crop,
                'general_tips': [
                    'Use quality planting materials',
                    'Apply appropriate fertilizers',
                    'Control pests and diseases',
                    'Maintain proper plant spacing',
                    'Harvest at correct time'
                ]
            }
    
    def get_care_calendar(self, crop):
        """Get monthly care calendar"""
        calendar = self.crop_care_calendar.get(crop.lower())
        if calendar:
            return {
                'crop': crop,
                'care_calendar': calendar
            }
        else:
            return {
                'crop': crop,
                'general_calendar': {
                    'planting': 'Start of rainy season',
                    'maintenance': 'Regular weeding and fertilizing',
                    'harvest': 'When crop reaches maturity'
                }
            }
    
    def get_natural_response_template(self, category, **kwargs):
        """Get a natural response template with variation"""
        templates = self.conversational_templates.get(category, [])
        if templates:
            template = random.choice(templates)
            return template.format(**kwargs)
        return None
    
    def get_all_crops(self):
        """Get list of all available crops in the database"""
        crops = set()
        databases = [self.diseases, self.fertilizers, self.planting_procedures, 
                    self.pests, self.yield_maximization, self.crop_care_calendar]
        
        for db in databases:
            crops.update(db.keys())
        
        return sorted(list(crops))

# Test the knowledge base
if __name__ == "__main__":
    kb = AgriculturalKnowledgeBase()
    
    print("Testing Agricultural Knowledge Base")
    print("=" * 50)
    
    # Test disease information
    print("1. DISEASE INFORMATION - Maize Streak Virus:")
    disease_info = kb.get_disease_info('maize', 'maize streak virus')
    if 'error' not in disease_info:
        info = disease_info['info']
        print("Symptoms:", ', '.join(info['symptoms']))
        print("Treatment:", ', '.join(info['treatment'][:2]))
        print("Prevention:", ', '.join(info['prevention'][:2]))
    
    # Test fertilizer recommendations
    print("\n2. FERTILIZER RECOMMENDATIONS - Maize:")
    fert_info = kb.get_fertilizer_recommendation('maize')
    program = fert_info['fertilizer_program']
    basal = program.get('basal_fertilizer', {})
    print(f"Basal fertilizer: {basal.get('npk', 'N/A')} at {basal.get('rate', 'N/A')}")
    print(f"Timing: {basal.get('timing', 'N/A')}")
    
    # Test planting guide
    print("\n3. PLANTING GUIDE - Maize:")
    planting_guide = kb.get_planting_guide('maize')
    if 'planting_guide' in planting_guide:
        land_prep = planting_guide['planting_guide']['land_preparation']
        print("Land preparation steps:")
        for i, step in enumerate(land_prep[:3], 1):
            print(f"  {i}. {step}")
        
        timeline = planting_guide['estimated_time']
        print(f"Time to harvest: {timeline.get('harvest', 'N/A')}")
    
    # Test pest information
    print("\n4. PEST INFORMATION - Fall Armyworm:")
    pest_info = kb.get_pest_info('maize', 'fall armyworm')
    if pest_info['info'] != 'Pest information not available':
        info = pest_info['info']
        print("Identification:", info['identification'])
        print("Control:", ', '.join(info['control'][:2]))
    
    # Test yield tips
    print("\n5. YIELD TIPS - Maize:")
    yield_info = kb.get_yield_tips('maize')
    tips = yield_info['yield_tips']
    for i, tip in enumerate(tips[:3], 1):
        print(f"  {i}. {tip}")
    
    # Test conversational templates
    print("\n6. CONVERSATIONAL TEMPLATES:")
    greeting = kb.get_natural_response_template('greetings', name='Farmer')
    print("Greeting:", greeting)
    
    # Test available crops
    print("\n7. AVAILABLE CROPS:")
    crops = kb.get_all_crops()
    print("Supported crops:", ', '.join(crops))
    
    print(f"\nTotal diseases in database: {len(kb.diseases)}")
    print(f"Total crops with fertilizer guides: {len(kb.fertilizers)}")
    print(f"Total crops with planting procedures: {len(kb.planting_procedures)}")