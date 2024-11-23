package com.example.onetry.resume.entity;

import com.example.onetry.resume.dto.req.ExperienceUpdateDto;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.OnDelete;
import org.hibernate.annotations.OnDeleteAction;

@Entity
@Getter
@Setter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name="experience")
public class Experience {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String companyName;
    private String employmentPeriod;
    private String lastPosition;
    private String responsibilities;

    @ManyToOne
    @JoinColumn(name = "resume_id")
    @OnDelete(action = OnDeleteAction.CASCADE)
    private Resume resume;

    @Builder
    private Experience(Resume resume) {
        this.resume = resume;
    }

    public void updateFromDto(ExperienceUpdateDto dto) {
        if (dto.companyName() != null) this.companyName = dto.companyName();
        if (dto.employmentPeriod() != null) this.employmentPeriod = dto.employmentPeriod();
        if (dto.lastPosition() != null) this.lastPosition = dto.lastPosition();
        if (dto.responsibilities() != null) this.responsibilities = dto.responsibilities();
    }
}
