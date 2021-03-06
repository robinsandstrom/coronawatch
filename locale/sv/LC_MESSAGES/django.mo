��          �   %   �      `  �  a     `     |     �     �  	   �     �     �               #     B     H  ,   a  	   �     �     �     �  !   �     �                *  �   E          -  k  2  �  �	     q     �  !   �  #   �     �     �       	   #     -     L     f  $   n  *   �     �     �     �     �     �     
          .     ?  �   W  
   �     
                             	   
                                                                                            
                    The hospital care needs in this model builds on an extended SEIR-model that simulates an epidemic
                    outbreak. People are divided into the groups S, E, Q, I, J, R, C and the flows inbetween the categories are decided
                    by the parameters. The preset parameters are a qualified guess, but they could change with time. To change a parameter with time,
                    please look at the code repo on github. For simplicity, we assume that people that are in intensive care have been hospitalized
                    and that no one dies outside of intensive care. We also assume that the rate of becoming healthy again is the same regardless if you
                    self-quarantine or not.
                 Asymptomatic infectiousness Average days as sick Average days in hospital Average days in intensive care Calculate Cases needing hospitalization Confirmed cases Dead Death rate in intensive care Estimate hospitalization needs Flows Future days to calculate Hospitalization cases needing intensive care Important In hospital In intensive care Incubation time Infected population in quarantine Infectiousness constant Isolated infectiousness Population factor Quarantined infectiousness Since the 12th of March, Swedish agencies stopped testing cases outside of
                            at-risk population. Look for trends in hospitalization or intensive care instead.
                             Unrecorded factor days Project-Id-Version: PACKAGE VERSION
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2020-04-03 01:19+0200
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language-Team: LANGUAGE <LL@li.org>
Language: 
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=2; plural=(n != 1);
 
Vårdbehoven i den här modellen bygger på en utvidgat SEIR-modell som simulerar ett epidemiskt utbrott. 
Människor delas in i grupperna S, E, Q, I, J, R, C och flödena mellan de olika kategorierna bestäms av 
 parametrarna som anges här. De förinställda parametrarna är en kvalificierad gissning men kan ändras med tiden 
 i och med att vi ändrar våra beteenden. För att ändra parametrar avseende på tid, ladda hem kod från GITHUB-repot. För enkelhetens skull antar vi att människor som intensivvårdas har tidigare vårdats i slutenvård, och att patienter enbart dör i intensivvården. Vi antar också att tillfrisknaden som sjuk är detsamma oavsett om man gått in i frivillig karantän eller inte. Asymptomatisk smittsamhet Genomsnittlig tid som sjuk Genomsnittlig tid på slutenvård Genomsnittlig tid på intensivvård Beräkna Fall som kräver slutenvård Bekräftade fall Dödsfall Andel som dör i intensivvård Uppskatta sjukvårdsbehov Flöden Antal dagar att beräkna i framtiden Slutenvårdsfall som kräver intensivvård Viktigt I slutenvård I intensivvård Inkubationstid Smittsamma i karantän Smittsamhet Smittsamhet på sjukhus Befolkningsandel Karantänad smittsamhet Sedan den 12e mars har samtliga regioner valt att sluta testa misstänkta fall utanför riskgrupper, försök hitta trender i dödsfall och vårdtillfällen istället. Mörkertal dagar 